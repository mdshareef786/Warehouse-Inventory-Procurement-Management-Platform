import math

from sqlalchemy.orm import Session

from app.models.supplier import Supplier

from app.repositories.supplier_repository import (
    SupplierRepository
)

from app.exceptions.custom_exceptions import (
    SupplierNotFoundException,
    SupplierEmailAlreadyExistsException,
    SupplierGSTAlreadyExistsException,
    SupplierSuspendedException,
    SupplierAlreadyActiveException,
)


class SupplierService:

    @staticmethod
    def create(
        db: Session,
        data
    ):

        existing_email = (
            SupplierRepository.get_by_email(
                db,
                data.email
            )
        )

        if existing_email:
            raise SupplierEmailAlreadyExistsException(
                "Supplier email already exists"
            )

        existing_gst = (
            SupplierRepository.get_by_gst(
                db,
                data.gst_number
            )
        )

        if existing_gst:
            raise SupplierGSTAlreadyExistsException(
                "Supplier GST number already exists"
            )

        supplier = Supplier(
            supplier_name=data.supplier_name,
            contact_person=data.contact_person,
            email=str(data.email).lower(),
            phone=data.phone,
            gst_number=data.gst_number.upper(),
            address=data.address,
            rating=data.rating,
            status="ACTIVE"
        )

        return SupplierRepository.create(
            db,
            supplier
        )

    @staticmethod
    def get_by_id(
        db: Session,
        supplier_id: int
    ):

        supplier = SupplierRepository.get_by_id(
            db,
            supplier_id
        )

        if not supplier:
            raise SupplierNotFoundException(
                "Supplier not found"
            )

        return supplier

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        search: str | None = None,
        status: str | None = None
    ):

        suppliers, total = (
            SupplierRepository.get_all(
                db=db,
                page=page,
                page_size=page_size,
                search=search,
                status=status
            )
        )

        total_pages = (
            math.ceil(total / page_size)
            if total
            else 0
        )

        return {
            "items": suppliers,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    @staticmethod
    def update(
        db: Session,
        supplier_id: int,
        data
    ):

        supplier = SupplierService.get_by_id(
            db,
            supplier_id
        )

        if supplier.status == "SUSPENDED":
            raise SupplierSuspendedException(
                "Suspended supplier cannot be updated"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "email" in update_data:

            existing = (
                SupplierRepository.get_by_email(
                    db,
                    str(update_data["email"]).lower()
                )
            )

            if existing and existing.id != supplier.id:
                raise SupplierEmailAlreadyExistsException(
                    "Supplier email already exists"
                )

            update_data["email"] = (
                str(update_data["email"]).lower()
            )

        if "gst_number" in update_data:

            gst_number = (
                update_data["gst_number"].upper()
            )

            existing = (
                SupplierRepository.get_by_gst(
                    db,
                    gst_number
                )
            )

            if existing and existing.id != supplier.id:
                raise SupplierGSTAlreadyExistsException(
                    "Supplier GST number already exists"
                )

            update_data["gst_number"] = gst_number

        for field, value in update_data.items():
            setattr(
                supplier,
                field,
                value
            )

        return SupplierRepository.update(
            db,
            supplier
        )

    @staticmethod
    def suspend(
        db: Session,
        supplier_id: int
    ):

        supplier = SupplierService.get_by_id(
            db,
            supplier_id
        )

        if supplier.status == "SUSPENDED":
            raise SupplierSuspendedException(
                "Supplier is already suspended"
            )

        supplier.status = "SUSPENDED"

        return SupplierRepository.update(
            db,
            supplier
        )

    @staticmethod
    def activate(
        db: Session,
        supplier_id: int
    ):

        supplier = SupplierService.get_by_id(
            db,
            supplier_id
        )

        if supplier.status == "ACTIVE":
            raise SupplierAlreadyActiveException(
                "Supplier is already active"
            )

        supplier.status = "ACTIVE"

        return SupplierRepository.update(
            db,
            supplier
        )