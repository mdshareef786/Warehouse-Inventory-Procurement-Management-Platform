from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles

from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    PurchaseOrderListResponse,
    PurchaseOrderReceiveRequest,
)

from app.services.purchase_order_service import (
    PurchaseOrderService
)


router = APIRouter(
    prefix="/purchase-orders",
    tags=["Purchase Orders"]
)


@router.post(
    "",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_purchase_order(
    data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return PurchaseOrderService.create(
        db=db,
        data=data,
        user_id=current_user.id
    )


@router.get(
    "",
    response_model=PurchaseOrderListResponse
)
def get_purchase_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        10,
        ge=1,
        le=100
    ),
    status: str | None = None,
    supplier_id: int | None = Query(
        None,
        gt=0
    ),
    warehouse_id: int | None = Query(
        None,
        gt=0
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return PurchaseOrderService.get_all(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        supplier_id=supplier_id,
        warehouse_id=warehouse_id
    )


@router.get(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponse
)
def get_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return PurchaseOrderService.get_by_id(
        db,
        purchase_order_id
    )


@router.post(
    "/{purchase_order_id}/submit",
    response_model=PurchaseOrderResponse
)
def submit_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return PurchaseOrderService.submit_for_approval(
        db,
        purchase_order_id
    )


@router.post(
    "/{purchase_order_id}/approve",
    response_model=PurchaseOrderResponse
)
def approve_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return PurchaseOrderService.approve(
        db=db,
        purchase_order_id=purchase_order_id,
        user_id=current_user.id
    )


@router.post(
    "/{purchase_order_id}/reject",
    response_model=PurchaseOrderResponse
)
def reject_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return PurchaseOrderService.reject(
        db,
        purchase_order_id
    )


@router.post(
    "/{purchase_order_id}/cancel",
    response_model=PurchaseOrderResponse
)
def cancel_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return PurchaseOrderService.cancel(
        db,
        purchase_order_id
    )
@router.post(
    "/{purchase_order_id}/order",
    response_model=PurchaseOrderResponse
)
def mark_purchase_order_ordered(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return PurchaseOrderService.mark_ordered(
        db,
        purchase_order_id
    )

@router.post(
    "/{purchase_order_id}/receive",
    response_model=PurchaseOrderResponse
)
def receive_purchase_order(
    purchase_order_id: int,
    data: PurchaseOrderReceiveRequest,
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
    return PurchaseOrderService.receive(
        db=db,
        purchase_order_id=purchase_order_id,
        data=data,
        user_id=current_user.id
    )