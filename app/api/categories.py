from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles

from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)

from app.services.category_service import (
    CategoryService
)


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return CategoryService.create(
        db,
        data
    )


@router.get(
    "",
    response_model=CategoryListResponse
)
def get_categories(
    page: int = Query(
        1,
        ge=1
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100
    ),
    search: str | None = None,
    is_active: bool | None = None,
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
    return CategoryService.get_all(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category(
    category_id: int,
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
    return CategoryService.get_by_id(
        db,
        category_id
    )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return CategoryService.update(
        db,
        category_id,
        data
    )


@router.delete(
    "/{category_id}",
    response_model=CategoryResponse
)
def archive_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return CategoryService.archive(
        db,
        category_id
    )


@router.post(
    "/{category_id}/activate",
    response_model=CategoryResponse
)
def activate_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return CategoryService.activate(
        db,
        category_id
    )