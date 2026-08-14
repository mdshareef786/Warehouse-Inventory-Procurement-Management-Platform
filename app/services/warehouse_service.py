import math

from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.repositories.warehouse_repository import (
    WarehouseRepository
)
from app.exceptions.custom_exceptions import (
    WarehouseNotFoundException,
    WarehouseCodeAlreadyExistsException,
    WarehouseDisabledException,
)

from app.repositories.user_repository import UserRepository

from app.exceptions.custom_exceptions import (
    WarehouseManagerNotFoundException,
    InvalidWarehouseManagerException,
    ManagerAlreadyAssignedException,
    WarehouseAlreadyActiveException
)


class WarehouseService:

    @staticmethod
    def create(
        db: Session,
        data
    ):

        existing = WarehouseRepository.get_by_code(
            db,
            data.code
        )

        if existing:
            raise WarehouseCodeAlreadyExistsException(
                "Warehouse code already exists"
            )

        warehouse = Warehouse(
            name=data.name,
            code=data.code.upper(),
            address=data.address,
            capacity=data.capacity,
            current_utilization=0,
            status="ACTIVE"
        )

        return WarehouseRepository.create(
            db,
            warehouse
        )

    @staticmethod
    def get_by_id(
        db: Session,
        warehouse_id: int
    ):

        warehouse = WarehouseRepository.get_by_id(
            db,
            warehouse_id
        )

        if not warehouse:
            raise WarehouseNotFoundException(
                "Warehouse not found"
            )

        return warehouse

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        search: str | None = None,
        status: str | None = None
    ):

        warehouses, total = (
            WarehouseRepository.get_all(
                db=db,
                page=page,
                page_size=page_size,
                search=search,
                status=status
            )
        )

        total_pages = math.ceil(
            total / page_size
        ) if total else 0

        return {
            "items": warehouses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    @staticmethod
    def update(
        db: Session,
        warehouse_id: int,
        data
    ):

        warehouse = WarehouseService.get_by_id(
            db,
            warehouse_id
        )

        if warehouse.status == "DISABLED":
            raise WarehouseDisabledException(
                "Disabled warehouse cannot be updated"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                warehouse,
                field,
                value
            )

        return WarehouseRepository.update(
            db,
            warehouse
        )

    @staticmethod
    def disable(
        db: Session,
        warehouse_id: int
    ):

        warehouse = WarehouseService.get_by_id(
            db,
            warehouse_id
        )

        if warehouse.status == "DISABLED":
            raise WarehouseDisabledException(
                "Warehouse is already disabled"
            )

        warehouse.status = "DISABLED"

        return WarehouseRepository.update(
            db,
            warehouse
        )

    @staticmethod
    def assign_manager(
        db: Session,
        warehouse_id: int,
        manager_id: int
    ):

        warehouse = WarehouseService.get_by_id(
            db,
            warehouse_id
        )

        if warehouse.status == "DISABLED":
            raise WarehouseDisabledException(
                "Cannot assign manager to a disabled warehouse"
            )

        manager = UserRepository.get_by_id(
            db,
            manager_id
        )

        if not manager:
            raise WarehouseManagerNotFoundException(
                "Manager user not found"
            )

        if not manager.is_active:
            raise InvalidWarehouseManagerException(
                "Manager account is inactive"
            )

        if not manager.role:
            raise InvalidWarehouseManagerException(
                "User does not have a role"
            )

        if manager.role.name != "WAREHOUSE_MANAGER":
            raise InvalidWarehouseManagerException(
                "Selected user is not a Warehouse Manager"
            )

        # Prevent assigning the same manager to another warehouse.
        if (
            manager.warehouse_id is not None
            and manager.warehouse_id != warehouse.id
        ):
            raise ManagerAlreadyAssignedException(
                "Manager is already assigned to another warehouse"
            )

        manager.warehouse_id = warehouse.id

        db.commit()
        db.refresh(manager)

        return warehouse

    @staticmethod
    def enable(
        db: Session,
        warehouse_id: int
    ):
        warehouse = WarehouseService.get_by_id(
            db,
            warehouse_id
        )

        if warehouse.status == "ACTIVE":
            raise WarehouseAlreadyActiveException(
                "Warehouse is already active"
            )

        warehouse.status = "ACTIVE"

        return WarehouseRepository.update(
            db,
            warehouse
        )

    