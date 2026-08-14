import math

from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.warehouse import Warehouse

from app.repositories.inventory_repository import (
    InventoryRepository,
)

from app.exceptions.custom_exceptions import (
    InventoryNotFoundException,
    ProductNotAvailableException,
    WarehouseNotAvailableException,
    InsufficientStockException,
    InsufficientReservedStockException,
)

from app.services.inventory_cache_service import (
    InventoryCacheService,
)

from app.services.alert_service import AlertService


class InventoryService:

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_product(
        db: Session,
        product_id: int,
    ):
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            raise ProductNotAvailableException(
                "Product not found"
            )

        if product.status != "ACTIVE":
            raise ProductNotAvailableException(
                "Product is not active"
            )

        return product

    @staticmethod
    def _validate_warehouse(
        db: Session,
        warehouse_id: int,
    ):
        warehouse = (
            db.query(Warehouse)
            .filter(Warehouse.id == warehouse_id)
            .first()
        )

        if not warehouse:
            raise WarehouseNotAvailableException(
                "Warehouse not found"
            )

        if warehouse.status != "ACTIVE":
            raise WarehouseNotAvailableException(
                "Warehouse is not active"
            )

        return warehouse

    # =========================================================
    # STOCK IN
    # =========================================================

    @staticmethod
    def stock_in(
        db: Session,
        product_id: int,
        warehouse_id: int,
        quantity: float,
        user_id: int,
        reason: str | None = None,
        reference_type: str | None = None,
        reference_id: int | None = None,
        commit: bool = True,
    ):
        """
        Add stock to inventory.

        Performs:
        - Product validation
        - Warehouse validation
        - Inventory creation if missing
        - Inventory quantity update
        - Transaction history
        - Low-stock alert check
        - Redis cache invalidation
        """

        if quantity <= 0:
            raise ValueError(
                "Stock-in quantity must be greater than zero"
            )

        InventoryService._validate_product(
            db,
            product_id,
        )

        InventoryService._validate_warehouse(
            db,
            warehouse_id,
        )

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                product_id,
                warehouse_id,
            )
        )

        if not inventory:
            inventory = Inventory(
                product_id=product_id,
                warehouse_id=warehouse_id,
                available_quantity=0,
                reserved_quantity=0,
                damaged_quantity=0,
            )

            InventoryRepository.create(
                db,
                inventory,
            )

        previous_quantity = (
            inventory.available_quantity
        )

        inventory.available_quantity += quantity

        InventoryRepository.update(
            db,
            inventory,
        )

        transaction = InventoryTransaction(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type="STOCK_IN",
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=inventory.available_quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason,
            performed_by=user_id,
        )

        InventoryRepository.create_transaction(
            db,
            transaction,
        )

        AlertService.check_inventory_alert(
            db=db,
            inventory=inventory,
        )

        if commit:
            db.commit()
            db.refresh(inventory)

            InventoryCacheService.invalidate_inventory(
                product_id=product_id,
                warehouse_id=warehouse_id,
            )

        return inventory

    # =========================================================
    # STOCK OUT
    # =========================================================

    @staticmethod
    def stock_out(
        db: Session,
        product_id: int,
        warehouse_id: int,
        quantity: float,
        user_id: int,
        reason: str | None = None,
        reference_type: str | None = None,
        reference_id: int | None = None,
        commit: bool = True,
    ):
        """
        Remove stock from inventory.
        """

        if quantity <= 0:
            raise ValueError(
                "Stock-out quantity must be greater than zero"
            )

        InventoryService._validate_product(
            db,
            product_id,
        )

        InventoryService._validate_warehouse(
            db,
            warehouse_id,
        )

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                product_id,
                warehouse_id,
            )
        )

        if not inventory:
            raise InventoryNotFoundException(
                "Inventory record not found"
            )

        if inventory.available_quantity < quantity:
            raise InsufficientStockException(
                "Insufficient available stock"
            )

        previous_quantity = (
            inventory.available_quantity
        )

        inventory.available_quantity -= quantity

        InventoryRepository.update(
            db,
            inventory,
        )

        transaction = InventoryTransaction(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type="STOCK_OUT",
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=inventory.available_quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason,
            performed_by=user_id,
        )

        InventoryRepository.create_transaction(
            db,
            transaction,
        )

        AlertService.check_inventory_alert(
            db=db,
            inventory=inventory,
        )

        if commit:
            db.commit()
            db.refresh(inventory)

            InventoryCacheService.invalidate_inventory(
                product_id=product_id,
                warehouse_id=warehouse_id,
            )

        return inventory

    # =========================================================
    # RESERVE STOCK
    # =========================================================

    @staticmethod
    def reserve(
        db: Session,
        product_id: int,
        warehouse_id: int,
        quantity: float,
        user_id: int,
        reason: str | None = None,
    ):
        """
        Reserve available inventory.
        """

        if quantity <= 0:
            raise ValueError(
                "Reservation quantity must be greater than zero"
            )

        InventoryService._validate_product(
            db,
            product_id,
        )

        InventoryService._validate_warehouse(
            db,
            warehouse_id,
        )

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                product_id,
                warehouse_id,
            )
        )

        if not inventory:
            raise InventoryNotFoundException(
                "Inventory record not found"
            )

        if inventory.available_quantity < quantity:
            raise InsufficientStockException(
                "Insufficient available stock for reservation"
            )

        previous_available = (
            inventory.available_quantity
        )

        inventory.available_quantity -= quantity
        inventory.reserved_quantity += quantity

        InventoryRepository.update(
            db,
            inventory,
        )

        transaction = InventoryTransaction(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type="RESERVE",
            quantity=quantity,
            previous_quantity=previous_available,
            new_quantity=inventory.available_quantity,
            reference_type="RESERVATION",
            reason=reason,
            performed_by=user_id,
        )

        InventoryRepository.create_transaction(
            db,
            transaction,
        )

        AlertService.check_inventory_alert(
            db=db,
            inventory=inventory,
        )

        db.commit()
        db.refresh(inventory)

        InventoryCacheService.invalidate_inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
        )

        return inventory

    # =========================================================
    # ADJUST INVENTORY
    # =========================================================

    @staticmethod
    def adjust(
        db: Session,
        product_id: int,
        warehouse_id: int,
        quantity: float,
        reason: str,
        user_id: int,
    ):
        """
        Set available inventory to the physical quantity.
        """

        if quantity < 0:
            raise ValueError(
                "Inventory quantity cannot be negative"
            )

        InventoryService._validate_product(
            db,
            product_id,
        )

        InventoryService._validate_warehouse(
            db,
            warehouse_id,
        )

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                product_id,
                warehouse_id,
            )
        )

        if not inventory:
            inventory = Inventory(
                product_id=product_id,
                warehouse_id=warehouse_id,
                available_quantity=0,
                reserved_quantity=0,
                damaged_quantity=0,
            )

            InventoryRepository.create(
                db,
                inventory,
            )

        previous_quantity = (
            inventory.available_quantity
        )

        inventory.available_quantity = quantity

        InventoryRepository.update(
            db,
            inventory,
        )

        transaction = InventoryTransaction(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type="ADJUSTMENT",
            quantity=quantity - previous_quantity,
            previous_quantity=previous_quantity,
            new_quantity=quantity,
            reason=reason,
            performed_by=user_id,
        )

        InventoryRepository.create_transaction(
            db,
            transaction,
        )

        AlertService.check_inventory_alert(
            db=db,
            inventory=inventory,
        )

        db.commit()
        db.refresh(inventory)

        InventoryCacheService.invalidate_inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
        )

        return inventory

    # =========================================================
    # PAGINATED INVENTORY
    # =========================================================

    @staticmethod
    def get_inventory(
        db: Session,
        page: int,
        page_size: int,
        product_id: int | None = None,
        warehouse_id: int | None = None,
    ):
        """
        Get paginated inventory.
        """

        items, total = (
            InventoryRepository.get_all(
                db=db,
                page=page,
                page_size=page_size,
                product_id=product_id,
                warehouse_id=warehouse_id,
            )
        )

        total_pages = (
            math.ceil(total / page_size)
            if total
            else 0
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    # =========================================================
    # INVENTORY HISTORY
    # =========================================================

    @staticmethod
    def get_history(
        db: Session,
        page: int,
        page_size: int,
        product_id: int | None = None,
        warehouse_id: int | None = None,
        transaction_type: str | None = None,
    ):
        """
        Get inventory transaction history.
        """

        items, total = (
            InventoryRepository.get_transactions(
                db=db,
                page=page,
                page_size=page_size,
                product_id=product_id,
                warehouse_id=warehouse_id,
                transaction_type=transaction_type,
            )
        )

        total_pages = (
            math.ceil(total / page_size)
            if total
            else 0
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    # =========================================================
    # SINGLE INVENTORY LOOKUP
    # =========================================================

    @staticmethod
    def get_inventory_item(
        db: Session,
        product_id: int,
        warehouse_id: int,
    ):
        """
        Get one inventory record.

        Cache strategy:
        1. Check Redis
        2. If hit → return cached data
        3. If miss → query PostgreSQL
        4. Store result in Redis
        5. Return database object
        """

        cached_inventory = (
            InventoryCacheService.get_inventory(
                product_id=product_id,
                warehouse_id=warehouse_id,
            )
        )

        if cached_inventory is not None:
            return cached_inventory

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db=db,
                product_id=product_id,
                warehouse_id=warehouse_id,
            )
        )

        if inventory is None:
            raise InventoryNotFoundException(
                "Inventory record not found"
            )

        InventoryCacheService.set_inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
            inventory=inventory,
        )

        return inventory

    # =========================================================
    # RELEASE RESERVED STOCK
    # =========================================================

    @staticmethod
    def release(
        db: Session,
        product_id: int,
        warehouse_id: int,
        quantity: float,
        user_id: int,
        reason: str | None = None,
    ):
        """
        Release previously reserved stock.
        """

        if quantity <= 0:
            raise ValueError(
                "Release quantity must be greater than zero"
            )

        InventoryService._validate_product(
            db,
            product_id,
        )

        InventoryService._validate_warehouse(
            db,
            warehouse_id,
        )

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                product_id,
                warehouse_id,
            )
        )

        if not inventory:
            raise InventoryNotFoundException(
                "Inventory record not found"
            )

        if inventory.reserved_quantity < quantity:
            raise InsufficientReservedStockException(
                "Insufficient reserved stock to release"
            )

        previous_available = (
            inventory.available_quantity
        )

        inventory.available_quantity += quantity
        inventory.reserved_quantity -= quantity

        InventoryRepository.update(
            db,
            inventory,
        )

        transaction = InventoryTransaction(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type="RELEASE",
            quantity=quantity,
            previous_quantity=previous_available,
            new_quantity=inventory.available_quantity,
            reference_type="RESERVATION",
            reason=reason,
            performed_by=user_id,
        )

        InventoryRepository.create_transaction(
            db,
            transaction,
        )

        AlertService.check_inventory_alert(
            db=db,
            inventory=inventory,
        )

        db.commit()
        db.refresh(inventory)

        InventoryCacheService.invalidate_inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
        )

        return inventory

    # =========================================================
    # DAMAGE STOCK
    # =========================================================

    @staticmethod
    def damage(
        db: Session,
        product_id: int,
        warehouse_id: int,
        quantity: float,
        user_id: int,
        reason: str,
    ):
        """
        Move available stock into damaged quantity.
        """

        if quantity <= 0:
            raise ValueError(
                "Damage quantity must be greater than zero"
            )

        InventoryService._validate_product(
            db,
            product_id,
        )

        InventoryService._validate_warehouse(
            db,
            warehouse_id,
        )

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                product_id,
                warehouse_id,
            )
        )

        if not inventory:
            raise InventoryNotFoundException(
                "Inventory record not found"
            )

        if inventory.available_quantity < quantity:
            raise InsufficientStockException(
                "Insufficient available stock for damage"
            )

        previous_quantity = (
            inventory.available_quantity
        )

        inventory.available_quantity -= quantity
        inventory.damaged_quantity += quantity

        InventoryRepository.update(
            db,
            inventory,
        )

        transaction = InventoryTransaction(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type="DAMAGE",
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=inventory.available_quantity,
            reference_type="DAMAGE",
            reason=reason,
            performed_by=user_id,
        )

        InventoryRepository.create_transaction(
            db,
            transaction,
        )

        AlertService.check_inventory_alert(
            db=db,
            inventory=inventory,
        )

        db.commit()
        db.refresh(inventory)

        InventoryCacheService.invalidate_inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
        )

        return inventory

    # =========================================================
    # INVENTORY RECONCILIATION
    # =========================================================

    @staticmethod
    def reconcile(
        db: Session,
        product_id: int,
        warehouse_id: int,
        physical_quantity: float,
        user_id: int,
        reason: str,
    ):
        """
        Reconcile system inventory against physical stock.

        physical_quantity includes:
        - available stock
        - reserved stock
        - damaged stock
        """

        if physical_quantity < 0:
            raise ValueError(
                "Physical quantity cannot be negative"
            )

        InventoryService._validate_product(
            db,
            product_id,
        )

        InventoryService._validate_warehouse(
            db,
            warehouse_id,
        )

        inventory = (
            InventoryRepository
            .get_by_product_and_warehouse(
                db,
                product_id,
                warehouse_id,
            )
        )

        if not inventory:
            raise InventoryNotFoundException(
                "Inventory record not found"
            )

        if physical_quantity < inventory.reserved_quantity:
            raise InsufficientReservedStockException(
                "Physical quantity cannot be less than reserved quantity"
            )

        previous_quantity = (
            inventory.available_quantity
        )

        new_available_quantity = (
            physical_quantity
            - inventory.reserved_quantity
            - inventory.damaged_quantity
        )

        if new_available_quantity < 0:
            raise ValueError(
                "Physical quantity is less than "
                "reserved and damaged stock"
            )

        difference = (
            new_available_quantity
            - previous_quantity
        )

        if difference == 0:
            return inventory

        inventory.available_quantity = (
            new_available_quantity
        )

        InventoryRepository.update(
            db,
            inventory,
        )

        transaction = InventoryTransaction(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type="RECONCILIATION",
            quantity=difference,
            previous_quantity=previous_quantity,
            new_quantity=new_available_quantity,
            reference_type="PHYSICAL_COUNT",
            reason=reason,
            performed_by=user_id,
        )

        InventoryRepository.create_transaction(
            db,
            transaction,
        )

        AlertService.check_inventory_alert(
            db=db,
            inventory=inventory,
        )

        db.commit()
        db.refresh(inventory)

        InventoryCacheService.invalidate_inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
        )
        
        return inventory