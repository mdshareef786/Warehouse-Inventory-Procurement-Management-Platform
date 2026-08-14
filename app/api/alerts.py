from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.dependencies.auth import require_roles

from app.services.alert_service import (
    AlertService,
)

from app.schemas.alert import (
    AlertResponse,
    AlertListResponse,
)


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.get(
    "",
    response_model=AlertListResponse,
)
def get_alerts(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),
    alert_type: str | None = None,
    is_acknowledged: bool | None = None,
    warehouse_id: int | None = None,
    product_id: int | None = None,
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

    return AlertService.get_alerts(
        db=db,
        page=page,
        page_size=page_size,
        alert_type=alert_type,
        is_acknowledged=is_acknowledged,
        warehouse_id=warehouse_id,
        product_id=product_id,
    )


@router.put(
    "/{alert_id}/acknowledge",
    response_model=AlertResponse,
)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN",
            "WAREHOUSE_MANAGER",
        )
    ),
):

    return AlertService.acknowledge(
        db=db,
        alert_id=alert_id,
    )