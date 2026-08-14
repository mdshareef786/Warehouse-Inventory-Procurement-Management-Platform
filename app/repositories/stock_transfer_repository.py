from sqlalchemy.orm import Session

from app.models.stock_transfer import (
    StockTransfer,
)


class StockTransferRepository:

    @staticmethod
    def create(
        db: Session,
        transfer: StockTransfer
    ):
        db.add(transfer)
        db.flush()

        return transfer

    @staticmethod
    def get_by_id(
        db: Session,
        transfer_id: int
    ):
        return (
            db.query(StockTransfer)
            .filter(
                StockTransfer.id == transfer_id
            )
            .first()
        )

    @staticmethod
    def get_by_transfer_number(
        db: Session,
        transfer_number: str
    ):
        return (
            db.query(StockTransfer)
            .filter(
                StockTransfer.transfer_number
                == transfer_number
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        status: str | None = None,
        source_warehouse_id: int | None = None,
        destination_warehouse_id: int | None = None,
    ):

        query = db.query(StockTransfer)

        if status:
            query = query.filter(
                StockTransfer.status
                == status.upper()
            )

        if source_warehouse_id is not None:
            query = query.filter(
                StockTransfer.source_warehouse_id
                == source_warehouse_id
            )

        if destination_warehouse_id is not None:
            query = query.filter(
                StockTransfer.destination_warehouse_id
                == destination_warehouse_id
            )

        total = query.count()

        offset = (
            (page - 1)
            * page_size
        )

        items = (
            query
            .order_by(
                StockTransfer.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    @staticmethod
    def update(
        db: Session,
        transfer: StockTransfer
    ):
        db.flush()

        return transfer