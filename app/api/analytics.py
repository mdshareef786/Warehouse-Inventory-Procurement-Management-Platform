from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.dependencies.auth import require_roles

from app.schemas.analytics import (
    DashboardAnalyticsResponse,
    InventoryAnalyticsResponse,
    SupplierAnalyticsResponse,
    WarehouseAnalyticsResponse,
)

from app.services.analytics_service import (
    AnalyticsService,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# =========================================================
# DASHBOARD
# =========================================================

@router.get(
    "/dashboard",
    response_model=DashboardAnalyticsResponse,
)
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "PROCUREMENT_OFFICER",
        )
    ),
):

    return AnalyticsService.get_dashboard(
        db
    )


# =========================================================
# INVENTORY
# =========================================================

@router.get(
    "/inventory",
    response_model=InventoryAnalyticsResponse,
)
def get_inventory_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
            "INVENTORY_STAFF",
        )
    ),
):

    return AnalyticsService.get_inventory(
        db
    )


# =========================================================
# SUPPLIERS
# =========================================================

@router.get(
    "/suppliers",
    response_model=SupplierAnalyticsResponse,
)
def get_supplier_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "PROCUREMENT_OFFICER",
            "WAREHOUSE_MANAGER",
        )
    ),
):

    return AnalyticsService.get_suppliers(
        db
    )


# =========================================================
# WAREHOUSES
# =========================================================

@router.get(
    "/warehouses",
    response_model=WarehouseAnalyticsResponse,
)
def get_warehouse_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
        )
    ),
):

    return AnalyticsService.get_warehouses(
        db
    )