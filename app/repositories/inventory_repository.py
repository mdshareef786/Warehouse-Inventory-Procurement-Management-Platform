from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction


class InventoryRepository:

    @staticmethod
    def get_by_product_and_warehouse(
        db: Session,
        product_id: int,
        warehouse_id: int,
    ):
        return (
            db.query(Inventory)
            .filter(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id,
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        inventory: Inventory,
    ):
        db.add(inventory)
        db.flush()
        return inventory

    @staticmethod
    def update(
        db: Session,
        inventory: Inventory,
    ):
        db.flush()
        return inventory

    @staticmethod
    def create_transaction(
        db: Session,
        transaction: InventoryTransaction,
    ):
        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        product_id: int | None = None,
        warehouse_id: int | None = None,
    ):
        query = db.query(Inventory)

        if product_id is not None:
            query = query.filter(
                Inventory.product_id == product_id
            )

        if warehouse_id is not None:
            query = query.filter(
                Inventory.warehouse_id == warehouse_id
            )

        total = query.with_entities(
            func.count(Inventory.id)
        ).scalar()

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(Inventory.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    @staticmethod
    def get_transactions(
        db: Session,
        page: int,
        page_size: int,
        product_id: int | None = None,
        warehouse_id: int | None = None,
        transaction_type: str | None = None,
    ):
        query = db.query(InventoryTransaction)

        if product_id is not None:
            query = query.filter(
                InventoryTransaction.product_id == product_id
            )

        if warehouse_id is not None:
            query = query.filter(
                InventoryTransaction.warehouse_id == warehouse_id
            )

        if transaction_type:
            query = query.filter(
                InventoryTransaction.transaction_type
                == transaction_type.upper()
            )

        total = query.with_entities(
            func.count(InventoryTransaction.id)
        ).scalar()

        offset = (page - 1) * page_size

        items = (
            query
            .order_by(
                InventoryTransaction.id.desc()
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total