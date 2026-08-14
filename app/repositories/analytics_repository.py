from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order import PurchaseOrderItem
from app.models.supplier import Supplier


class AnalyticsRepository:

    # =========================================================
    # PRODUCTS
    # =========================================================

    @staticmethod
    def get_total_products(db: Session):

        return (
            db.query(
                func.count(Product.id)
            )
            .filter(
                Product.status == "ACTIVE"
            )
            .scalar()
            or 0
        )

    # =========================================================
    # WAREHOUSES
    # =========================================================

    @staticmethod
    def get_total_warehouses(db: Session):

        return (
            db.query(
                func.count(Warehouse.id)
            )
            .filter(
                Warehouse.status == "ACTIVE"
            )
            .scalar()
            or 0
        )

    # =========================================================
    # INVENTORY SUMMARY
    # =========================================================

    @staticmethod
    def get_inventory_summary(
        db: Session
    ):

        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        Inventory.available_quantity
                    ),
                    0
                ),
                func.coalesce(
                    func.sum(
                        Inventory.reserved_quantity
                    ),
                    0
                ),
                func.coalesce(
                    func.sum(
                        Inventory.damaged_quantity
                    ),
                    0
                )
            )
            .select_from(Inventory)
            .first()
        )

        return {
            "available": float(
                result[0] or 0
            ),
            "reserved": float(
                result[1] or 0
            ),
            "damaged": float(
                result[2] or 0
            ),
        }

    # =========================================================
    # INVENTORY VALUE
    # =========================================================

    @staticmethod
    def get_inventory_value(
        db: Session
    ):

        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        Inventory.available_quantity
                        * Product.cost_price
                    ),
                    0
                )
            )
            .select_from(Inventory)
            .join(
                Product,
                Product.id == Inventory.product_id
            )
            .filter(
                Product.status == "ACTIVE"
            )
            .scalar()
        )

        return float(
            result or 0
        )

    # =========================================================
    # LOW STOCK
    # =========================================================

    @staticmethod
    def get_low_stock_count(
        db: Session
    ):

        return (
            db.query(
                func.count(Inventory.id)
            )
            .select_from(Inventory)
            .join(
                Product,
                Product.id == Inventory.product_id
            )
            .filter(
                Product.status == "ACTIVE",
                Inventory.available_quantity
                <= Product.reorder_level,
                Inventory.available_quantity > 0
            )
            .scalar()
            or 0
        )

    # =========================================================
    # OUT OF STOCK
    # =========================================================

    @staticmethod
    def get_out_of_stock_count(
        db: Session
    ):

        return (
            db.query(
                func.count(Inventory.id)
            )
            .select_from(Inventory)
            .join(
                Product,
                Product.id == Inventory.product_id
            )
            .filter(
                Product.status == "ACTIVE",
                Inventory.available_quantity <= 0
            )
            .scalar()
            or 0
        )

    # =========================================================
    # PURCHASE ORDERS THIS MONTH
    # =========================================================

    @staticmethod
    def get_purchase_orders_this_month(
        db: Session
    ):

        now = datetime.now()

        start_of_month = datetime(
            now.year,
            now.month,
            1
        )

        return (
            db.query(
                func.count(PurchaseOrder.id)
            )
            .filter(
                PurchaseOrder.order_date
                >= start_of_month
            )
            .scalar()
            or 0
        )

    # =========================================================
    # INVENTORY TURNOVER
    # =========================================================

    @staticmethod
    def get_inventory_turnover(
        db: Session
    ):

        stock_out = (
            db.query(
                func.coalesce(
                    func.sum(
                        func.abs(
                            InventoryTransaction.quantity
                        )
                    ),
                    0
                )
            )
            .select_from(
                InventoryTransaction
            )
            .filter(
                InventoryTransaction.transaction_type
                == "STOCK_OUT"
            )
            .scalar()
        )

        inventory_value = (
            AnalyticsRepository
            .get_inventory_value(db)
        )

        if inventory_value <= 0:
            return 0.0

        turnover = (
            float(stock_out or 0)
            / inventory_value
        )

        return round(
            turnover,
            4
        )

    # =========================================================
    # MOST MOVED PRODUCTS
    # =========================================================

    @staticmethod
    def get_most_moved_products(
        db: Session,
        limit: int = 10
    ):

        results = (
            db.query(
                Product.id,
                Product.sku,
                Product.product_name,
                func.coalesce(
                    func.sum(
                        func.abs(
                            InventoryTransaction.quantity
                        )
                    ),
                    0
                ).label(
                    "movement_quantity"
                )
            )
            .select_from(Product)
            .join(
                InventoryTransaction,
                InventoryTransaction.product_id
                == Product.id
            )
            .filter(
                Product.status == "ACTIVE"
            )
            .group_by(
                Product.id,
                Product.sku,
                Product.product_name
            )
            .order_by(
                func.sum(
                    func.abs(
                        InventoryTransaction.quantity
                    )
                ).desc()
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": row.id,

                "sku": row.sku,

                "product_name":
                    row.product_name,

                "movement_quantity":
                    float(
                        row.movement_quantity or 0
                    ),
            }
            for row in results
        ]

    # =========================================================
    # SUPPLIER PERFORMANCE
    # =========================================================

    @staticmethod
    def get_supplier_performance(
        db: Session
    ):

        suppliers = (
            db.query(Supplier)
            .order_by(
                Supplier.id
            )
            .all()
        )

        response = []

        for supplier in suppliers:

            # -----------------------------------------
            # Purchase order count
            # -----------------------------------------

            po_count = (
                db.query(
                    func.count(
                        PurchaseOrder.id
                    )
                )
                .select_from(
                    PurchaseOrder
                )
                .filter(
                    PurchaseOrder.supplier_id
                    == supplier.id
                )
                .scalar()
                or 0
            )

            # -----------------------------------------
            # Ordered quantity
            # -----------------------------------------

            ordered_quantity = (
                db.query(
                    func.coalesce(
                        func.sum(
                            PurchaseOrderItem.quantity
                        ),
                        0
                    )
                )
                .select_from(
                    PurchaseOrderItem
                )
                .join(
                    PurchaseOrder,
                    PurchaseOrder.id
                    == PurchaseOrderItem.purchase_order_id
                )
                .filter(
                    PurchaseOrder.supplier_id
                    == supplier.id
                )
                .scalar()
                or 0
            )

            # -----------------------------------------
            # Received quantity
            # -----------------------------------------

            received_quantity = (
                db.query(
                    func.coalesce(
                        func.sum(
                            PurchaseOrderItem.received_quantity
                        ),
                        0
                    )
                )
                .select_from(
                    PurchaseOrderItem
                )
                .join(
                    PurchaseOrder,
                    PurchaseOrder.id
                    == PurchaseOrderItem.purchase_order_id
                )
                .filter(
                    PurchaseOrder.supplier_id
                    == supplier.id
                )
                .scalar()
                or 0
            )

            # -----------------------------------------
            # Fulfillment rate
            # -----------------------------------------

            if ordered_quantity > 0:

                fulfillment_rate = (
                    float(received_quantity)
                    / float(ordered_quantity)
                ) * 100

            else:

                fulfillment_rate = 0.0

            response.append(
                {
                    "supplier_id":
                        supplier.id,

                    "supplier_name":
                        supplier.supplier_name,

                    "rating":
                        float(
                            supplier.rating or 0
                        ),

                    "status":
                        supplier.status,

                    "purchase_orders":
                        po_count,

                    "ordered_quantity":
                        float(
                            ordered_quantity
                        ),

                    "received_quantity":
                        float(
                            received_quantity
                        ),

                    "fulfillment_rate":
                        round(
                            fulfillment_rate,
                            2
                        ),
                }
            )

        return response

    # =========================================================
    # WAREHOUSE ANALYTICS
    # =========================================================

    @staticmethod
    def get_warehouse_analytics(
        db: Session
    ):

        warehouses = (
            db.query(Warehouse)
            .filter(
                Warehouse.status == "ACTIVE"
            )
            .order_by(
                Warehouse.id
            )
            .all()
        )

        results = []

        for warehouse in warehouses:

            # -----------------------------------------
            # Inventory value
            # -----------------------------------------

            inventory_value = (
                db.query(
                    func.coalesce(
                        func.sum(
                            Inventory.available_quantity
                            * Product.cost_price
                        ),
                        0
                    )
                )
                .select_from(Inventory)
                .join(
                    Product,
                    Product.id
                    == Inventory.product_id
                )
                .filter(
                    Inventory.warehouse_id
                    == warehouse.id,
                    Product.status == "ACTIVE"
                )
                .scalar()
            )

            # -----------------------------------------
            # Total available quantity
            # -----------------------------------------

            total_quantity = (
                db.query(
                    func.coalesce(
                        func.sum(
                            Inventory.available_quantity
                        ),
                        0
                    )
                )
                .select_from(Inventory)
                .filter(
                    Inventory.warehouse_id
                    == warehouse.id
                )
                .scalar()
            )

            # -----------------------------------------
            # Capacity
            # -----------------------------------------

            capacity = float(
                warehouse.capacity or 0
            )

            # -----------------------------------------
            # Current utilization
            # -----------------------------------------

            current_utilization = float(
                warehouse.current_utilization
                or 0
            )

            # -----------------------------------------
            # Utilization percentage
            #
            # Example:
            #
            # capacity = 10000
            # utilization = 4500
            #
            # percentage = 45%
            # -----------------------------------------

            if capacity > 0:

                utilization_percentage = (
                    current_utilization
                    / capacity
                ) * 100

            else:

                utilization_percentage = 0.0

            # -----------------------------------------
            # Safety boundaries
            # -----------------------------------------

            utilization_percentage = min(
                max(
                    utilization_percentage,
                    0.0
                ),
                100.0
            )

            # -----------------------------------------
            # Result
            # -----------------------------------------

            results.append(
                {
                    "warehouse_id":
                        warehouse.id,

                    "warehouse_name":
                        warehouse.name,

                    "warehouse_code":
                        warehouse.code,

                    "capacity":
                        capacity,

                    "current_utilization":
                        current_utilization,

                    "utilization_percentage":
                        round(
                            utilization_percentage,
                            2
                        ),

                    "total_quantity":
                        float(
                            total_quantity or 0
                        ),

                    "inventory_value":
                        float(
                            inventory_value or 0
                        ),

                    "status":
                        warehouse.status,
                }
            )

        return results

    # =========================================================
    # INVENTORY ANALYTICS
    # =========================================================

    @staticmethod
    def get_inventory_analytics(
        db: Session
    ):

        summary = (
            AnalyticsRepository
            .get_inventory_summary(db)
        )

        inventory_value = (
            AnalyticsRepository
            .get_inventory_value(db)
        )

        low_stock = (
            AnalyticsRepository
            .get_low_stock_count(db)
        )

        out_of_stock = (
            AnalyticsRepository
            .get_out_of_stock_count(db)
        )

        total_records = (
            db.query(
                func.count(
                    Inventory.id
                )
            )
            .select_from(Inventory)
            .scalar()
            or 0
        )

        most_moved = (
            AnalyticsRepository
            .get_most_moved_products(db)
        )

        return {
            "total_inventory_records":
                total_records,

            "total_available_quantity":
                summary["available"],

            "total_reserved_quantity":
                summary["reserved"],

            "total_damaged_quantity":
                summary["damaged"],

            "inventory_value":
                inventory_value,

            "low_stock_items":
                low_stock,

            "out_of_stock_items":
                out_of_stock,

            "most_moved_products":
                most_moved,
        }