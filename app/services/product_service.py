import math

from sqlalchemy.orm import Session

from app.models.product import Product

from app.repositories.product_repository import (
    ProductRepository
)

from app.repositories.category_repository import (
    CategoryRepository
)

from app.exceptions.custom_exceptions import (
    ProductNotFoundException,
    ProductSKUAlreadyExistsException,
    ProductBarcodeAlreadyExistsException,
    ProductCategoryNotFoundException,
    ProductArchivedException,
    ProductAlreadyActiveException,
)


class ProductService:

    @staticmethod
    def create(
        db: Session,
        data
    ):

        sku = data.sku.strip().upper()

        existing_sku = (
            ProductRepository.get_by_sku(
                db,
                sku
            )
        )

        if existing_sku:
            raise ProductSKUAlreadyExistsException(
                "Product SKU already exists"
            )

        category = CategoryRepository.get_by_id(
            db,
            data.category_id
        )

        if not category:
            raise ProductCategoryNotFoundException(
                "Product category not found"
            )

        if not category.is_active:
            raise ProductCategoryNotFoundException(
                "Cannot assign product to archived category"
            )

        barcode = data.barcode

        if barcode:

            barcode = barcode.strip()

            existing_barcode = (
                ProductRepository.get_by_barcode(
                    db,
                    barcode
                )
            )

            if existing_barcode:
                raise ProductBarcodeAlreadyExistsException(
                    "Product barcode already exists"
                )

        product = Product(
            sku=sku,
            product_name=data.product_name.strip(),
            category_id=data.category_id,
            brand=data.brand,
            unit=data.unit,
            cost_price=data.cost_price,
            selling_price=data.selling_price,
            reorder_level=data.reorder_level,
            barcode=barcode,
            status="ACTIVE"
        )

        return ProductRepository.create(
            db,
            product
        )

    @staticmethod
    def get_by_id(
        db: Session,
        product_id: int
    ):

        product = ProductRepository.get_by_id(
            db,
            product_id
        )

        if not product:
            raise ProductNotFoundException(
                "Product not found"
            )

        return product

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        search: str | None = None,
        category_id: int | None = None,
        status: str | None = None
    ):

        products, total = (
            ProductRepository.get_all(
                db=db,
                page=page,
                page_size=page_size,
                search=search,
                category_id=category_id,
                status=status
            )
        )

        total_pages = (
            math.ceil(total / page_size)
            if total
            else 0
        )

        return {
            "items": products,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    @staticmethod
    def update(
        db: Session,
        product_id: int,
        data
    ):

        product = ProductService.get_by_id(
            db,
            product_id
        )

        if product.status == "ARCHIVED":
            raise ProductArchivedException(
                "Archived product cannot be updated"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "sku" in update_data:

            sku = update_data["sku"].strip().upper()

            existing = ProductRepository.get_by_sku(
                db,
                sku
            )

            if existing and existing.id != product.id:
                raise ProductSKUAlreadyExistsException(
                    "Product SKU already exists"
                )

            update_data["sku"] = sku

        if "barcode" in update_data:

            barcode = update_data["barcode"]

            if barcode:

                barcode = barcode.strip()

                existing = (
                    ProductRepository.get_by_barcode(
                        db,
                        barcode
                    )
                )

                if existing and existing.id != product.id:
                    raise ProductBarcodeAlreadyExistsException(
                        "Product barcode already exists"
                    )

                update_data["barcode"] = barcode

        if "category_id" in update_data:

            category = CategoryRepository.get_by_id(
                db,
                update_data["category_id"]
            )

            if not category:
                raise ProductCategoryNotFoundException(
                    "Product category not found"
                )

            if not category.is_active:
                raise ProductCategoryNotFoundException(
                    "Cannot assign product to archived category"
                )

        for field, value in update_data.items():
            setattr(
                product,
                field,
                value
            )

        return ProductRepository.update(
            db,
            product
        )

    @staticmethod
    def archive(
        db: Session,
        product_id: int
    ):

        product = ProductService.get_by_id(
            db,
            product_id
        )

        if product.status == "ARCHIVED":
            raise ProductArchivedException(
                "Product is already archived"
            )

        product.status = "ARCHIVED"

        return ProductRepository.update(
            db,
            product
        )

    @staticmethod
    def activate(
        db: Session,
        product_id: int
    ):

        product = ProductService.get_by_id(
            db,
            product_id
        )

        if product.status == "ACTIVE":
            raise ProductAlreadyActiveException(
                "Product is already active"
            )

        product.status = "ACTIVE"

        return ProductRepository.update(
            db,
            product
        )