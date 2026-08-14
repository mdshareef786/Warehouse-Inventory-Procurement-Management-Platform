from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:

    @staticmethod
    def create(
        db: Session,
        product: Product
    ):
        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    @staticmethod
    def get_by_id(
        db: Session,
        product_id: int
    ):
        return (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

    @staticmethod
    def get_by_sku(
        db: Session,
        sku: str
    ):
        return (
            db.query(Product)
            .filter(Product.sku == sku)
            .first()
        )

    @staticmethod
    def get_by_barcode(
        db: Session,
        barcode: str
    ):
        return (
            db.query(Product)
            .filter(Product.barcode == barcode)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        search: str | None = None,
        category_id: int | None = None,
        status: str | None = None
    ):
        query = db.query(Product)

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Product.sku.ilike(search_value)
                | Product.product_name.ilike(search_value)
                | Product.brand.ilike(search_value)
                | Product.barcode.ilike(search_value)
            )

        if category_id is not None:
            query = query.filter(
                Product.category_id == category_id
            )

        if status:
            query = query.filter(
                Product.status == status.upper()
            )

        total = query.with_entities(
            func.count(Product.id)
        ).scalar()

        offset = (page - 1) * page_size

        products = (
            query
            .order_by(Product.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return products, total

    @staticmethod
    def update(
        db: Session,
        product: Product
    ):
        db.commit()
        db.refresh(product)

        return product