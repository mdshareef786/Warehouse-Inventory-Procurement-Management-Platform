import math

from sqlalchemy.orm import Session

from app.models.category import Category

from app.repositories.category_repository import (
    CategoryRepository
)

from app.exceptions.custom_exceptions import (
    CategoryNotFoundException,
    CategoryAlreadyExistsException,
    CategoryArchivedException,
    CategoryAlreadyActiveException,
)


class CategoryService:

    @staticmethod
    def create(
        db: Session,
        data
    ):
        name = data.name.strip()

        existing = CategoryRepository.get_by_name(
            db,
            name
        )

        if existing:
            raise CategoryAlreadyExistsException(
                "Category already exists"
            )

        category = Category(
            name=name,
            description=data.description,
            is_active=True
        )

        return CategoryRepository.create(
            db,
            category
        )

    @staticmethod
    def get_by_id(
        db: Session,
        category_id: int
    ):
        category = CategoryRepository.get_by_id(
            db,
            category_id
        )

        if not category:
            raise CategoryNotFoundException(
                "Category not found"
            )

        return category

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        search: str | None = None,
        is_active: bool | None = None
    ):
        categories, total = (
            CategoryRepository.get_all(
                db=db,
                page=page,
                page_size=page_size,
                search=search,
                is_active=is_active
            )
        )

        total_pages = (
            math.ceil(total / page_size)
            if total
            else 0
        )

        return {
            "items": categories,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    @staticmethod
    def update(
        db: Session,
        category_id: int,
        data
    ):
        category = CategoryService.get_by_id(
            db,
            category_id
        )

        if not category.is_active:
            raise CategoryArchivedException(
                "Archived category cannot be updated"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "name" in update_data:
            name = update_data["name"].strip()

            existing = CategoryRepository.get_by_name(
                db,
                name
            )

            if existing and existing.id != category.id:
                raise CategoryAlreadyExistsException(
                    "Category name already exists"
                )

            update_data["name"] = name

        for field, value in update_data.items():
            setattr(
                category,
                field,
                value
            )

        return CategoryRepository.update(
            db,
            category
        )

    @staticmethod
    def archive(
        db: Session,
        category_id: int
    ):
        category = CategoryService.get_by_id(
            db,
            category_id
        )

        if not category.is_active:
            raise CategoryArchivedException(
                "Category is already archived"
            )

        category.is_active = False

        return CategoryRepository.update(
            db,
            category
        )

    @staticmethod
    def activate(
        db: Session,
        category_id: int
    ):
        category = CategoryService.get_by_id(
            db,
            category_id
        )

        if category.is_active:
            raise CategoryAlreadyActiveException(
                "Category is already active"
            )

        category.is_active = True

        return CategoryRepository.update(
            db,
            category
        )