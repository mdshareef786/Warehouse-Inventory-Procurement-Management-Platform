from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles

from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierListResponse,
)

from app.services.supplier_service import (
    SupplierService
)


router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


@router.post(
    "",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED
)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return SupplierService.create(
        db,
        data
    )


@router.get(
    "",
    response_model=SupplierListResponse
)
def get_suppliers(
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
            "PROCUREMENT_OFFICER",
            "WAREHOUSE_MANAGER"
        )
    )
):
    return SupplierService.get_all(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        status=status
    )


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "PROCUREMENT_OFFICER",
            "WAREHOUSE_MANAGER"
        )
    )
):
    return SupplierService.get_by_id(
        db,
        supplier_id
    )


@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return SupplierService.update(
        db,
        supplier_id,
        data
    )


@router.delete(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def suspend_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "PROCUREMENT_OFFICER"
        )
    )
):
    return SupplierService.suspend(
        db,
        supplier_id
    )


@router.post(
    "/{supplier_id}/activate",
    response_model=SupplierResponse
)
def activate_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("SUPER_ADMIN")
    )
):
    return SupplierService.activate(
        db,
        supplier_id
    )