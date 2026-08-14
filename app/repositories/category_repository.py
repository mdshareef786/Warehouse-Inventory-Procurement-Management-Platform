from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:

    @staticmethod
    def create(
        db: Session,
        category: Category
    ):
        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def get_by_id(
        db: Session,
        category_id: int
    ):
        return (
            db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        name: str
    ):
        return (
            db.query(Category)
            .filter(Category.name == name)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        search: str | None = None,
        is_active: bool | None = None
    ):
        query = db.query(Category)

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Category.name.ilike(search_value)
                | Category.description.ilike(search_value)
            )

        if is_active is not None:
            query = query.filter(
                Category.is_active == is_active
            )

        total = query.with_entities(
            func.count(Category.id)
        ).scalar()

        offset = (page - 1) * page_size

        categories = (
            query
            .order_by(Category.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return categories, total

    @staticmethod
    def update(
        db: Session,
        category: Category
    ):
        db.commit()
        db.refresh(category)

        return category