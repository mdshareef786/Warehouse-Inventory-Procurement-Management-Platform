from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseResponse,
    WarehouseUpdate,
    WarehouseListResponse,
    WarehouseManagerAssign,
)

from app.services.warehouse_service import WarehouseService


router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"]
)


@router.post(
    "",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_warehouse(
    data: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return WarehouseService.create(
        db,
        data
    )


@router.get(
    "",
    response_model=WarehouseListResponse
)
def get_warehouses(
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
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER"
        )
    )
):
    return WarehouseService.get_all(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        status=status
    )


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseResponse
)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER"
        )
    )
):
    return WarehouseService.get_by_id(
        db,
        warehouse_id
    )


@router.put(
    "/{warehouse_id}",
    response_model=WarehouseResponse
)
def update_warehouse(
    warehouse_id: int,
    data: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return WarehouseService.update(
        db,
        warehouse_id,
        data
    )


@router.delete(
    "/{warehouse_id}",
    response_model=WarehouseResponse
)
def disable_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return WarehouseService.disable(
        db,
        warehouse_id
    )

@router.put(
    "/{warehouse_id}/manager",
    response_model=WarehouseResponse
)
def assign_manager(
    warehouse_id: int,
    data: WarehouseManagerAssign,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return WarehouseService.assign_manager(
        db=db,
        warehouse_id=warehouse_id,
        manager_id=data.manager_id
    )

@router.post(
    "/{warehouse_id}/enable",
    response_model=WarehouseResponse
)
def enable_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return WarehouseService.enable(
        db,
        warehouse_id
    )