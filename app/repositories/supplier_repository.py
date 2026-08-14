from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.supplier import Supplier


class SupplierRepository:

    @staticmethod
    def create(
        db: Session,
        supplier: Supplier
    ):
        db.add(supplier)
        db.commit()
        db.refresh(supplier)

        return supplier

    @staticmethod
    def get_by_id(
        db: Session,
        supplier_id: int
    ):
        return (
            db.query(Supplier)
            .filter(Supplier.id == supplier_id)
            .first()
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ):
        return (
            db.query(Supplier)
            .filter(Supplier.email == email)
            .first()
        )

    @staticmethod
    def get_by_gst(
        db: Session,
        gst_number: str
    ):
        return (
            db.query(Supplier)
            .filter(
                Supplier.gst_number == gst_number
            )
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
        query = db.query(Supplier)

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Supplier.supplier_name.ilike(search_value)
                | Supplier.contact_person.ilike(search_value)
                | Supplier.email.ilike(search_value)
                | Supplier.gst_number.ilike(search_value)
                | Supplier.phone.ilike(search_value)
            )

        if status:
            query = query.filter(
                Supplier.status == status.upper()
            )

        total = query.with_entities(
            func.count(Supplier.id)
        ).scalar()

        offset = (page - 1) * page_size

        suppliers = (
            query
            .order_by(Supplier.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return suppliers, total

    @staticmethod
    def update(
        db: Session,
        supplier: Supplier
    ):
        db.commit()
        db.refresh(supplier)

        return supplier