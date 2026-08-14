import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
)
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse

from app.repositories.purchase_order_repository import (
    PurchaseOrderRepository
)

from app.services.inventory_service import InventoryService

from app.exceptions.custom_exceptions import (
    PurchaseOrderNotFoundException,
    PurchaseOrderAlreadyExistsException,
    InvalidPurchaseOrderStatusException,
    PurchaseOrderAlreadyApprovedException,
    PurchaseOrderRejectedException,
    PurchaseOrderCancelledException,
    PurchaseOrderAlreadyReceivedException,
    InvalidPurchaseOrderReceiveException,
    InvalidPurchaseOrderItemException,
    SupplierNotAvailableException,
    ProductNotAvailableException,
    WarehouseNotAvailableException,
)


class PurchaseOrderService:

    @staticmethod
    def _generate_po_number():
        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d%H%M%S%f")

        return f"PO-{timestamp}"

    @staticmethod
    def create(
        db: Session,
        data,
        user_id: int
    ):

        supplier = (
            db.query(Supplier)
            .filter(
                Supplier.id == data.supplier_id
            )
            .first()
        )

        if not supplier:
            raise SupplierNotAvailableException(
                "Supplier not found"
            )

        if supplier.status != "ACTIVE":
            raise SupplierNotAvailableException(
                "Cannot create purchase order for suspended supplier"
            )

        warehouse = (
            db.query(Warehouse)
            .filter(
                Warehouse.id == data.warehouse_id
            )
            .first()
        )

        if not warehouse:
            raise WarehouseNotAvailableException(
                "Warehouse not found"
            )

        if warehouse.status != "ACTIVE":
            raise WarehouseNotAvailableException(
                "Warehouse is not active"
            )

        po_number = (
            PurchaseOrderService._generate_po_number()
        )

        purchase_order = PurchaseOrder(
            po_number=po_number,
            supplier_id=data.supplier_id,
            warehouse_id=data.warehouse_id,
            expected_delivery_date=(
                data.expected_delivery_date
            ),
            status="DRAFT",
            total_amount=0,
            created_by=user_id
        )

        total_amount = 0

        product_ids = [
            item.product_id
            for item in data.items
        ]

        if len(product_ids) != len(set(product_ids)):
            raise InvalidPurchaseOrderItemException(
                "Duplicate products are not allowed in a purchase order"
            )

        for item_data in data.items:

            product = (
                db.query(Product)
                .filter(
                    Product.id
                    == item_data.product_id
                )
                .first()
            )

            if not product:
                raise ProductNotAvailableException(
                    f"Product {item_data.product_id} not found"
                )

            if product.status != "ACTIVE":
                raise ProductNotAvailableException(
                    f"Product {item_data.product_id} is not active"
                )

            item_total = (
                item_data.quantity
                * item_data.unit_price
            )

            item = PurchaseOrderItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                received_quantity=0,
                unit_price=item_data.unit_price,
                total_price=item_total
            )

            purchase_order.items.append(item)

            total_amount += item_total

        purchase_order.total_amount = total_amount

        PurchaseOrderRepository.create(
                        db,
                        purchase_order
                    )

        db.commit()
        db.refresh(purchase_order)

        return purchase_order

    @staticmethod
    def get_by_id(
        db: Session,
        purchase_order_id: int
    ):

        po = PurchaseOrderRepository.get_by_id(
            db,
            purchase_order_id
        )

        if not po:
            raise PurchaseOrderNotFoundException(
                "Purchase order not found"
            )

        return po

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        status: str | None = None,
        supplier_id: int | None = None,
        warehouse_id: int | None = None
    ):

        items, total = (
            PurchaseOrderRepository.get_all(
                db=db,
                page=page,
                page_size=page_size,
                status=status,
                supplier_id=supplier_id,
                warehouse_id=warehouse_id
            )
        )

        total_pages = (
            math.ceil(total / page_size)
            if total
            else 0
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    @staticmethod
    def submit_for_approval(
        db: Session,
        purchase_order_id: int
    ):

        po = PurchaseOrderService.get_by_id(
            db,
            purchase_order_id
        )

        if po.status != "DRAFT":
            raise InvalidPurchaseOrderStatusException(
                "Only draft purchase orders can be submitted"
            )

        po.status = "PENDING_APPROVAL"

        db.commit()
        db.refresh(po)

        return po

    @staticmethod
    def approve(
        db: Session,
        purchase_order_id: int,
        user_id: int
    ):

        po = PurchaseOrderService.get_by_id(
            db,
            purchase_order_id
        )

        if po.status != "PENDING_APPROVAL":
            raise InvalidPurchaseOrderStatusException(
                "Only pending purchase orders can be approved"
            )

        po.status = "APPROVED"
        po.approved_by = user_id
        po.approved_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(po)

        return po

    @staticmethod
    def reject(
        db: Session,
        purchase_order_id: int
    ):

        po = PurchaseOrderService.get_by_id(
            db,
            purchase_order_id
        )

        if po.status != "PENDING_APPROVAL":
            raise InvalidPurchaseOrderStatusException(
                "Only pending purchase orders can be rejected"
            )

        po.status = "REJECTED"

        db.commit()
        db.refresh(po)

        return po

    @staticmethod
    def cancel(
        db: Session,
        purchase_order_id: int
    ):

        po = PurchaseOrderService.get_by_id(
            db,
            purchase_order_id
        )

        if po.status in (
            "COMPLETED",
            "CANCELLED"
        ):
            raise InvalidPurchaseOrderStatusException(
                "Purchase order cannot be cancelled"
            )

        po.status = "CANCELLED"

        db.commit()
        db.refresh(po)

        return po

    @staticmethod
    def mark_ordered(
        db: Session,
        purchase_order_id: int
    ):
        po = PurchaseOrderService.get_by_id(
            db,
            purchase_order_id
        )

        if po.status != "APPROVED":
            raise InvalidPurchaseOrderStatusException(
                "Only approved purchase orders can be marked as ordered"
            )

        po.status = "ORDERED"

        db.commit()
        db.refresh(po)

        return po

    @staticmethod
    def receive(
        db: Session,
        purchase_order_id: int,
        data,
        user_id: int,
    ):
        po = PurchaseOrderService.get_by_id(
            db,
            purchase_order_id
        )

        if po.status not in (
            "ORDERED",
            "PARTIALLY_RECEIVED"
        ):
            raise InvalidPurchaseOrderStatusException(
                "Only ordered or partially received purchase orders "
                "can receive stock"
            )

        receive_product_ids = [
            item.product_id
            for item in data.items
        ]

        if len(receive_product_ids) != len(
            set(receive_product_ids)
        ):
            raise InvalidPurchaseOrderReceiveException(
                "Duplicate products are not allowed in a receiving request"
            )

        po_items = {
            item.product_id: item
            for item in po.items
        }

        # Validate everything BEFORE changing inventory
        for receive_item in data.items:

            po_item = po_items.get(
                receive_item.product_id
            )

            if not po_item:
                raise InvalidPurchaseOrderItemException(
                    f"Product {receive_item.product_id} "
                    f"is not part of purchase order "
                    f"{purchase_order_id}"
                )

            remaining_quantity = (
                po_item.quantity
                - po_item.received_quantity
            )

            if receive_item.quantity > remaining_quantity:
                raise InvalidPurchaseOrderReceiveException(
                    f"Cannot receive {receive_item.quantity} "
                    f"units of product "
                    f"{receive_item.product_id}. "
                    f"Remaining quantity is "
                    f"{remaining_quantity}"
                )

        try:

            for receive_item in data.items:

                po_item = po_items[
                    receive_item.product_id
                ]

                # Update received quantity
                po_item.received_quantity += (
                    receive_item.quantity
                )

                # Add stock to inventory
                InventoryService.stock_in(
                    db=db,
                    product_id=receive_item.product_id,
                    warehouse_id=po.warehouse_id,
                    quantity=receive_item.quantity,
                    user_id=user_id,
                    reason=(
                        f"Purchase Order "
                        f"{po.po_number} received"
                    ),
                    reference_type="PURCHASE_ORDER",
                    reference_id=po.id,
                    commit=False,
                )

            # Check whether everything has been received
            all_received = all(
                item.received_quantity >= item.quantity
                for item in po.items
            )

            if all_received:
                po.status = "RECEIVED"
            else:
                po.status = "PARTIALLY_RECEIVED"

            db.commit()
            db.refresh(po)

            return po

        except Exception:
            db.rollback()
            raise