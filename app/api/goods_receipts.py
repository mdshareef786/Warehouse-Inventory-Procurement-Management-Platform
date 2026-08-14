from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.dependencies.auth import (
    require_roles,
)

from app.schemas.goods_receipt import (
    GoodsReceiptCreate,
    GoodsReceiptResponse,
    GoodsReceiptListResponse,
)

from app.services.goods_receipt_service import (
    GoodsReceiptService,
)


router = APIRouter(
    prefix="/goods-receipts",
    tags=["Goods Receipts"],
)


@router.post(
    "",
    response_model=GoodsReceiptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_goods_receipt(
    data: GoodsReceiptCreate,
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
    return GoodsReceiptService.create(
        db=db,
        purchase_order_id=(
            data.purchase_order_id
        ),
        data=data,
        user_id=current_user.id,
    )


@router.get(
    "",
    response_model=GoodsReceiptListResponse,
)
def get_goods_receipts(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),
    purchase_order_id: int | None = Query(
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
    return GoodsReceiptService.get_all(
        db=db,
        page=page,
        page_size=page_size,
        purchase_order_id=(
            purchase_order_id
        ),
        warehouse_id=warehouse_id,
    )


@router.get(
    "/{receipt_id}",
    response_model=GoodsReceiptResponse,
)
def get_goods_receipt(
    receipt_id: int,
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
    return GoodsReceiptService.get_by_id(
        db=db,
        receipt_id=receipt_id,
    )