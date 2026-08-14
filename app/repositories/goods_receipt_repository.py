from sqlalchemy.orm import Session

from app.models.goods_receipt import GoodsReceipt


class GoodsReceiptRepository:

    @staticmethod
    def create(
        db: Session,
        receipt: GoodsReceipt,
    ):
        db.add(receipt)
        db.flush()

        return receipt

    @staticmethod
    def get_by_id(
        db: Session,
        receipt_id: int,
    ):
        return (
            db.query(GoodsReceipt)
            .filter(
                GoodsReceipt.id == receipt_id
            )
            .first()
        )

    @staticmethod
    def get_by_receipt_number(
        db: Session,
        receipt_number: str,
    ):
        return (
            db.query(GoodsReceipt)
            .filter(
                GoodsReceipt.receipt_number
                == receipt_number
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        purchase_order_id: int | None = None,
        warehouse_id: int | None = None,
    ):
        query = db.query(GoodsReceipt)

        if purchase_order_id is not None:
            query = query.filter(
                GoodsReceipt.purchase_order_id
                == purchase_order_id
            )

        if warehouse_id is not None:
            query = query.filter(
                GoodsReceipt.warehouse_id
                == warehouse_id
            )

        total = query.count()

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(
                GoodsReceipt.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total