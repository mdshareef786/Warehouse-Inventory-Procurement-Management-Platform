from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
)


class PurchaseOrderRepository:

    @staticmethod
    def create(
        db: Session,
        purchase_order: PurchaseOrder
    ):
        db.add(purchase_order)
        db.flush()

        return purchase_order

    @staticmethod
    def get_by_id(
        db: Session,
        purchase_order_id: int
    ):
        return (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.id
                == purchase_order_id
            )
            .first()
        )

    @staticmethod
    def get_by_po_number(
        db: Session,
        po_number: str
    ):
        return (
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.po_number
                == po_number
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        status: str | None = None,
        supplier_id: int | None = None,
        warehouse_id: int | None = None
    ):
        query = db.query(PurchaseOrder)

        if status:
            query = query.filter(
                PurchaseOrder.status == status.upper()
            )

        if supplier_id is not None:
            query = query.filter(
                PurchaseOrder.supplier_id == supplier_id
            )

        if warehouse_id is not None:
            query = query.filter(
                PurchaseOrder.warehouse_id == warehouse_id
            )

        total = query.count()

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(PurchaseOrder.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total
    @staticmethod
    def update(
        db: Session,
        purchase_order: PurchaseOrder
    ):
        db.flush()

        return purchase_order