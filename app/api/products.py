from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

from app.services.product_service import (
    ProductService
)


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return ProductService.create(
        db,
        data
    )


@router.get(
    "",
    response_model=ProductListResponse
)
def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        10,
        ge=1,
        le=100
    ),
    search: str | None = None,
    category_id: int | None = Query(
        None,
        gt=0
    ),
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER",
            "INVENTORY_STAFF"
        )
    )
):
    return ProductService.get_all(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        status=status
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER",
            "INVENTORY_STAFF"
        )
    )
):
    return ProductService.get_by_id(
        db,
        product_id
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return ProductService.update(
        db,
        product_id,
        data
    )


@router.delete(
    "/{product_id}",
    response_model=ProductResponse
)
def archive_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return ProductService.archive(
        db,
        product_id
    )


@router.post(
    "/{product_id}/activate",
    response_model=ProductResponse
)
def activate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return ProductService.activate(
        db,
        product_id
    )