import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.goods_receipt import (
    GoodsReceipt,
    GoodsReceiptItem,
)

from app.models.purchase_order import PurchaseOrder

from app.repositories.goods_receipt_repository import (
    GoodsReceiptRepository,
)

from app.services.inventory_service import (
    InventoryService,
)

from app.exceptions.custom_exceptions import (
    PurchaseOrderNotFoundException,
    InvalidPurchaseOrderStatusException,
    InvalidPurchaseOrderItemException,
    InvalidPurchaseOrderReceiveException,
)


class GoodsReceiptService:

    @staticmethod
    def _generate_receipt_number():
        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d%H%M%S%f")

        return f"GR-{timestamp}"

    @staticmethod
    def create(
        db: Session,
        purchase_order_id: int,
        data,
        user_id: int,
    ):
        # -----------------------------------------------------
        # 1. Get Purchase Order
        # -----------------------------------------------------

        purchase_order = (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.id
                == purchase_order_id
            )
            .first()
        )

        if not purchase_order:
            raise PurchaseOrderNotFoundException(
                "Purchase order not found"
            )

        # -----------------------------------------------------
        # 2. Validate PO status
        # -----------------------------------------------------

        if purchase_order.status not in (
            "ORDERED",
            "PARTIALLY_RECEIVED",
        ):
            raise InvalidPurchaseOrderStatusException(
                "Goods can only be received for "
                "ORDERED or PARTIALLY_RECEIVED "
                "purchase orders"
            )

        # -----------------------------------------------------
        # 3. Prevent duplicate products
        # -----------------------------------------------------

        product_ids = [
            item.product_id
            for item in data.items
        ]

        if len(product_ids) != len(
            set(product_ids)
        ):
            raise InvalidPurchaseOrderItemException(
                "Duplicate products are not allowed "
                "in a goods receipt"
            )

        # -----------------------------------------------------
        # 4. Map PO items
        # -----------------------------------------------------

        po_items = {
            item.product_id: item
            for item in purchase_order.items
        }

        # -----------------------------------------------------
        # 5. Validate EVERYTHING before modifying DB
        # -----------------------------------------------------

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
                    f"Cannot receive "
                    f"{receive_item.quantity} units of "
                    f"product {receive_item.product_id}. "
                    f"Remaining quantity is "
                    f"{remaining_quantity}"
                )

        # -----------------------------------------------------
        # 6. Create receipt
        # -----------------------------------------------------

        receipt = GoodsReceipt(
            receipt_number=(
                GoodsReceiptService
                ._generate_receipt_number()
            ),
            purchase_order_id=purchase_order.id,
            warehouse_id=purchase_order.warehouse_id,
            received_by=user_id,
            total_quantity=0,
            status="RECEIVED",
        )

        total_quantity = 0

        try:

            # -------------------------------------------------
            # 7. Process each received item
            # -------------------------------------------------

            for receive_item in data.items:

                po_item = po_items[
                    receive_item.product_id
                ]

                # Update PO received quantity
                po_item.received_quantity += (
                    receive_item.quantity
                )

                # Add receipt item
                receipt_item = GoodsReceiptItem(
                    product_id=(
                        receive_item.product_id
                    ),
                    quantity=(
                        receive_item.quantity
                    ),
                )

                receipt.items.append(
                    receipt_item
                )

                total_quantity += (
                    receive_item.quantity
                )

                # Update inventory
                InventoryService.stock_in(
                    db=db,
                    product_id=(
                        receive_item.product_id
                    ),
                    warehouse_id=(
                        purchase_order.warehouse_id
                    ),
                    quantity=(
                        receive_item.quantity
                    ),
                    user_id=user_id,
                    reason=(
                        f"Goods Receipt "
                        f"{receipt.receipt_number}"
                    ),
                    reference_type="GOODS_RECEIPT",
                    reference_id=None,
                    commit=False,
                )

            # -------------------------------------------------
            # 8. Update PO status
            # -------------------------------------------------

            all_received = all(
                item.received_quantity
                >= item.quantity
                for item in purchase_order.items
            )

            if all_received:
                purchase_order.status = "RECEIVED"
            else:
                purchase_order.status = (
                    "PARTIALLY_RECEIVED"
                )

            # -------------------------------------------------
            # 9. Set receipt total
            # -------------------------------------------------

            receipt.total_quantity = total_quantity

            db.add(receipt)

            db.flush()

            # -------------------------------------------------
            # 10. Commit everything atomically
            # -------------------------------------------------

            db.commit()

            db.refresh(receipt)

            return receipt

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_by_id(
        db: Session,
        receipt_id: int,
    ):
        receipt = (
            GoodsReceiptRepository.get_by_id(
                db,
                receipt_id,
            )
        )

        if not receipt:
            raise ValueError(
                "Goods receipt not found"
            )

        return receipt

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        purchase_order_id: int | None = None,
        warehouse_id: int | None = None,
    ):
        items, total = (
            GoodsReceiptRepository.get_all(
                db=db,
                page=page,
                page_size=page_size,
                purchase_order_id=(
                    purchase_order_id
                ),
                warehouse_id=warehouse_id,
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
            "total_pages": total_pages,
        }