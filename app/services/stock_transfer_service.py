import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.stock_transfer import (
    StockTransfer,
    StockTransferItem,
)
from app.models.product import Product
from app.models.warehouse import Warehouse

from app.repositories.stock_transfer_repository import (
    StockTransferRepository,
)

from app.services.inventory_service import (
    InventoryService,
)

from app.exceptions.custom_exceptions import (
    TransferNotFoundException,
    InvalidTransferException,
    TransferAlreadyApprovedException,
    TransferAlreadyRejectedException,
    TransferNotReadyException,
    InsufficientStockException,
    SameWarehouseTransferException,
    ProductNotAvailableException,
    WarehouseNotAvailableException,
)


class StockTransferService:

    # =========================================================
    # TRANSFER NUMBER
    # =========================================================

    @staticmethod
    def _generate_transfer_number():

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d%H%M%S%f")

        return f"TR-{timestamp}"

    # =========================================================
    # VALIDATE WAREHOUSE
    # =========================================================

    @staticmethod
    def _validate_warehouse(
        db: Session,
        warehouse_id: int,
    ):

        warehouse = (
            db.query(Warehouse)
            .filter(
                Warehouse.id == warehouse_id
            )
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
    # VALIDATE PRODUCT
    # =========================================================

    @staticmethod
    def _validate_product(
        db: Session,
        product_id: int,
    ):

        product = (
            db.query(Product)
            .filter(
                Product.id == product_id
            )
            .first()
        )

        if not product:
            raise ProductNotAvailableException(
                f"Product {product_id} not found"
            )

        if product.status != "ACTIVE":
            raise ProductNotAvailableException(
                f"Product {product_id} is not active"
            )

        return product

    # =========================================================
    # CREATE TRANSFER
    # =========================================================

    @staticmethod
    def create(
        db: Session,
        data,
        user_id: int,
    ):

        # -----------------------------------------------------
        # Validate warehouses
        # -----------------------------------------------------

        if (
            data.source_warehouse_id
            == data.destination_warehouse_id
        ):
            raise SameWarehouseTransferException(
                "Source and destination warehouses "
                "cannot be the same"
            )

        StockTransferService._validate_warehouse(
            db,
            data.source_warehouse_id,
        )

        StockTransferService._validate_warehouse(
            db,
            data.destination_warehouse_id,
        )

        # -----------------------------------------------------
        # Validate items
        # -----------------------------------------------------

        if not data.items:
            raise InvalidTransferException(
                "Transfer must contain at least one product"
            )

        product_ids = set()

        for item_data in data.items:

            if item_data.product_id in product_ids:
                raise InvalidTransferException(
                    f"Product {item_data.product_id} "
                    "appears more than once"
                )

            product_ids.add(
                item_data.product_id
            )

            StockTransferService._validate_product(
                db,
                item_data.product_id,
            )

        # -----------------------------------------------------
        # Generate transfer number
        # -----------------------------------------------------

        transfer_number = (
            StockTransferService
            ._generate_transfer_number()
        )

        # -----------------------------------------------------
        # Create transfer
        # -----------------------------------------------------

        transfer = StockTransfer(
            transfer_number=transfer_number,
            source_warehouse_id=(
                data.source_warehouse_id
            ),
            destination_warehouse_id=(
                data.destination_warehouse_id
            ),
            requested_by=user_id,
            status="REQUESTED",
        )

        # -----------------------------------------------------
        # Create transfer items
        # -----------------------------------------------------

        for item_data in data.items:

            item = StockTransferItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                received_quantity=0,
            )

            transfer.items.append(item)

        StockTransferRepository.create(
            db,
            transfer,
        )

        db.commit()

        db.refresh(transfer)

        return transfer

    # =========================================================
    # GET BY ID
    # =========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        transfer_id: int,
    ):

        transfer = (
            StockTransferRepository.get_by_id(
                db,
                transfer_id,
            )
        )

        if not transfer:
            raise TransferNotFoundException(
                "Stock transfer not found"
            )

        return transfer

    # =========================================================
    # GET ALL
    # =========================================================

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int,
        status: str | None = None,
        source_warehouse_id: int | None = None,
        destination_warehouse_id: int | None = None,
    ):

        items, total = (
            StockTransferRepository.get_all(
                db=db,
                page=page,
                page_size=page_size,
                status=status,
                source_warehouse_id=(
                    source_warehouse_id
                ),
                destination_warehouse_id=(
                    destination_warehouse_id
                ),
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
    # APPROVE TRANSFER
    # =========================================================

    @staticmethod
    def approve(
        db: Session,
        transfer_id: int,
        user_id: int,
    ):

        transfer = (
            StockTransferService.get_by_id(
                db,
                transfer_id,
            )
        )

        if transfer.status == "APPROVED":
            raise TransferAlreadyApprovedException(
                "Transfer is already approved"
            )

        if transfer.status != "REQUESTED":
            raise InvalidTransferException(
                "Only requested transfers can be approved"
            )

        # -----------------------------------------------------
        # Validate source stock before approval
        # -----------------------------------------------------

        for item in transfer.items:

            inventory = (
                InventoryService
                .get_inventory_item(
                    db=db,
                    product_id=item.product_id,
                    warehouse_id=(
                        transfer.source_warehouse_id
                    ),
                )
            )

            if not inventory:
                raise InvalidTransferException(
                    f"No inventory found for product "
                    f"{item.product_id} in source warehouse"
                )

            if (
                inventory.available_quantity
                < item.quantity
            ):
                raise InsufficientStockException(
                    f"Insufficient stock for product "
                    f"{item.product_id}"
                )

        transfer.status = "APPROVED"

        transfer.approved_by = user_id

        transfer.approved_at = (
            datetime.now(timezone.utc)
        )

        db.commit()

        db.refresh(transfer)

        return transfer

    # =========================================================
    # REJECT TRANSFER
    # =========================================================

    @staticmethod
    def reject(
        db: Session,
        transfer_id: int,
    ):

        transfer = (
            StockTransferService.get_by_id(
                db,
                transfer_id,
            )
        )

        if transfer.status == "REJECTED":
            raise TransferAlreadyRejectedException(
                "Transfer is already rejected"
            )

        if transfer.status != "REQUESTED":
            raise InvalidTransferException(
                "Only requested transfers can be rejected"
            )

        transfer.status = "REJECTED"

        db.commit()

        db.refresh(transfer)

        return transfer

    # =========================================================
    # DISPATCH / SHIP TRANSFER
    # =========================================================

    @staticmethod
    def dispatch(
        db: Session,
        transfer_id: int,
        user_id: int,
    ):

        transfer = (
            StockTransferService.get_by_id(
                db,
                transfer_id,
            )
        )

        if transfer.status != "APPROVED":
            raise TransferNotReadyException(
                "Only approved transfers can be dispatched"
            )

        # -----------------------------------------------------
        # Deduct stock from source warehouse
        # -----------------------------------------------------

        for item in transfer.items:

            InventoryService.stock_out(
                db=db,
                product_id=item.product_id,
                warehouse_id=(
                    transfer.source_warehouse_id
                ),
                quantity=item.quantity,
                user_id=user_id,
                reason=(
                    f"Stock transfer "
                    f"{transfer.transfer_number}"
                ),
                reference_type="STOCK_TRANSFER",
                reference_id=transfer.id,
                commit=False,
            )

        transfer.status = "IN_TRANSIT"

        db.commit()

        db.refresh(transfer)

        return transfer

    # =========================================================
    # RECEIVE TRANSFER
    # =========================================================

    @staticmethod
    def receive(
        db: Session,
        transfer_id: int,
        user_id: int,
    ):

        transfer = (
            StockTransferService.get_by_id(
                db,
                transfer_id,
            )
        )

        if transfer.status != "IN_TRANSIT":
            raise TransferNotReadyException(
                "Only in-transit transfers can be received"
            )

        # -----------------------------------------------------
        # Add stock to destination warehouse
        # -----------------------------------------------------

        for item in transfer.items:

            InventoryService.stock_in(
                db=db,
                product_id=item.product_id,
                warehouse_id=(
                    transfer.destination_warehouse_id
                ),
                quantity=item.quantity,
                user_id=user_id,
                reason=(
                    f"Stock transfer "
                    f"{transfer.transfer_number} received"
                ),
                reference_type="STOCK_TRANSFER",
                reference_id=transfer.id,
                commit=False,
            )

            item.received_quantity = item.quantity

        transfer.status = "RECEIVED"

        transfer.received_at = (
            datetime.now(timezone.utc)
        )

        db.commit()

        db.refresh(transfer)

        return transfer