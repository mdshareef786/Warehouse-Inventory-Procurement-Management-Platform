from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles

from app.schemas.inventory import (
    StockInRequest,
    StockOutRequest,
    InventoryAdjustRequest,
    InventoryReserveRequest,
    InventoryReleaseRequest,
    InventoryDamageRequest,
    InventoryReconciliationRequest,
    InventoryResponse,
    InventoryTransactionResponse,
    InventoryListResponse,
    InventoryTransactionListResponse,
)

from app.services.inventory_service import (
    InventoryService,
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


# =========================================================
# GET ALL INVENTORY
# =========================================================

@router.get(
    "",
    response_model=InventoryListResponse,
)
def get_inventory(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),
    product_id: int | None = Query(
        None,
        gt=0,
    ),
    warehouse_id: int | None = Query(
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
    return InventoryService.get_inventory(
        db=db,
        page=page,
        page_size=page_size,
        product_id=product_id,
        warehouse_id=warehouse_id,
    )


# =========================================================
# GET SINGLE INVENTORY
# REDIS CACHE ENABLED
# =========================================================

@router.get(
    "/{product_id}/{warehouse_id}",
    response_model=InventoryResponse,
)
def get_inventory_item(
    product_id: int,
    warehouse_id: int,
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
    return InventoryService.get_inventory_item(
        db=db,
        product_id=product_id,
        warehouse_id=warehouse_id,
    )


# =========================================================
# STOCK IN
# =========================================================

@router.post(
    "/stock-in",
    response_model=InventoryResponse,
)
def stock_in(
    data: StockInRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
        )
    ),
):
    return InventoryService.stock_in(
        db=db,
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        quantity=data.quantity,
        user_id=current_user.id,
        reason=data.reason,
    )


# =========================================================
# STOCK OUT
# =========================================================

@router.post(
    "/stock-out",
    response_model=InventoryResponse,
)
def stock_out(
    data: StockOutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
        )
    ),
):
    return InventoryService.stock_out(
        db=db,
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        quantity=data.quantity,
        user_id=current_user.id,
        reason=data.reason,
    )


# =========================================================
# ADJUST INVENTORY
# =========================================================

@router.post(
    "/adjust",
    response_model=InventoryResponse,
)
def adjust_inventory(
    data: InventoryAdjustRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
        )
    ),
):
    return InventoryService.adjust(
        db=db,
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        quantity=data.quantity,
        reason=data.reason,
        user_id=current_user.id,
    )


# =========================================================
# INVENTORY HISTORY
# =========================================================

@router.get(
    "/history",
    response_model=InventoryTransactionListResponse
)
def inventory_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        10,
        ge=1,
        le=100
    ),
    product_id: int | None = Query(
        None,
        gt=0
    ),
    warehouse_id: int | None = Query(
        None,
        gt=0
    ),
    transaction_type: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return InventoryService.get_history(
        db=db,
        page=page,
        page_size=page_size,
        product_id=product_id,
        warehouse_id=warehouse_id,
        transaction_type=transaction_type
    )

# =========================================================
# RESERVE INVENTORY
# =========================================================

@router.post(
    "/reserve",
    response_model=InventoryResponse,
)
def reserve_inventory(
    data: InventoryReserveRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
        )
    ),
):
    return InventoryService.reserve(
        db=db,
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        quantity=data.quantity,
        user_id=current_user.id,
        reason=data.reason,
    )


# =========================================================
# RELEASE RESERVED INVENTORY
# =========================================================

@router.post(
    "/release",
    response_model=InventoryResponse,
)
def release_inventory(
    data: InventoryReleaseRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
        )
    ),
):
    return InventoryService.release(
        db=db,
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        quantity=data.quantity,
        user_id=current_user.id,
        reason=data.reason,
    )


# =========================================================
# DAMAGE INVENTORY
# =========================================================

@router.post(
    "/damage",
    response_model=InventoryResponse,
)
def damage_inventory(
    data: InventoryDamageRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
        )
    ),
):
    return InventoryService.damage(
        db=db,
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        quantity=data.quantity,
        user_id=current_user.id,
        reason=data.reason,
    )


# =========================================================
# RECONCILE INVENTORY
# =========================================================

@router.post(
    "/reconcile",
    response_model=InventoryResponse,
)
def reconcile_inventory(
    data: InventoryReconciliationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
        )
    ),
):
    return InventoryService.reconcile(
        db=db,
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        physical_quantity=data.physical_quantity,
        user_id=current_user.id,
        reason=data.reason,
    )