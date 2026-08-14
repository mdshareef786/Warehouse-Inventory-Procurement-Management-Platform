from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse


class WarehouseRepository:

    @staticmethod
    def create(
        db: Session,
        warehouse: Warehouse
    ):
        db.add(warehouse)
        db.commit()
        db.refresh(warehouse)

        return warehouse

    @staticmethod
    def get_by_id(
        db: Session,
        warehouse_id: int
    ):
        return (
            db.query(Warehouse)
            .filter(Warehouse.id == warehouse_id)
            .first()
        )

    @staticmethod
    def get_by_code(
        db: Session,
        code: str
    ):
        return (
            db.query(Warehouse)
            .filter(Warehouse.code == code)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        search: str | None = None,
        status: str | None = None
    ):
        query = db.query(Warehouse)

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Warehouse.name.ilike(search_value)
                | Warehouse.code.ilike(search_value)
                | Warehouse.address.ilike(search_value)
            )

        if status:
            query = query.filter(
                Warehouse.status == status.upper()
            )

        total = query.with_entities(
            func.count(Warehouse.id)
        ).scalar()

        offset = (page - 1) * page_size

        warehouses = (
            query
            .order_by(Warehouse.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return warehouses, total

    @staticmethod
    def update(
        db: Session,
        warehouse: Warehouse
    ):
        db.commit()
        db.refresh(warehouse)

        return warehouse