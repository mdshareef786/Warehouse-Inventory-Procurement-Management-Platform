from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles

from app.schemas.stock_transfer import (
    StockTransferCreate,
    StockTransferResponse,
    StockTransferListResponse,
)

from app.services.stock_transfer_service import (
    StockTransferService,
)


router = APIRouter(
    prefix="/transfers",
    tags=["Stock Transfers"],
)


# =========================================================
# CREATE TRANSFER
# =========================================================

@router.post(
    "",
    response_model=StockTransferResponse,
)
def create_transfer(
    data: StockTransferCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
        )
    ),
):
    return StockTransferService.create(
        db=db,
        data=data,
        user_id=current_user.id,
    )


# =========================================================
# GET ALL TRANSFERS
# =========================================================

@router.get(
    "",
    response_model=StockTransferListResponse,
)
def get_transfers(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),
    status: str | None = None,
    source_warehouse_id: int | None = Query(
        None,
        gt=0,
    ),
    destination_warehouse_id: int | None = Query(
        None,
        gt=0,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
            "PROCUREMENT_OFFICER",
        )
    ),
):
    return StockTransferService.get_all(
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


# =========================================================
# GET TRANSFER BY ID
# =========================================================

@router.get(
    "/{transfer_id}",
    response_model=StockTransferResponse,
)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
            "PROCUREMENT_OFFICER",
        )
    ),
):
    return StockTransferService.get_by_id(
        db=db,
        transfer_id=transfer_id,
    )


# =========================================================
# APPROVE TRANSFER
# =========================================================

@router.post(
    "/{transfer_id}/approve",
    response_model=StockTransferResponse,
)
def approve_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
        )
    ),
):
    return StockTransferService.approve(
        db=db,
        transfer_id=transfer_id,
        user_id=current_user.id,
    )


# =========================================================
# REJECT TRANSFER
# =========================================================

@router.post(
    "/{transfer_id}/reject",
    response_model=StockTransferResponse,
)
def reject_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
        )
    ),
):
    return StockTransferService.reject(
        db=db,
        transfer_id=transfer_id,
    )


# =========================================================
# DISPATCH TRANSFER
# =========================================================

@router.post(
    "/{transfer_id}/dispatch",
    response_model=StockTransferResponse,
)
def dispatch_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
        )
    ),
):
    return StockTransferService.dispatch(
        db=db,
        transfer_id=transfer_id,
        user_id=current_user.id,
    )


# =========================================================
# RECEIVE TRANSFER
# =========================================================

@router.post(
    "/{transfer_id}/receive",
    response_model=StockTransferResponse,
)
def receive_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
        )
    ),
):
    return StockTransferService.receive(
        db=db,
        transfer_id=transfer_id,
        user_id=current_user.id,
    )