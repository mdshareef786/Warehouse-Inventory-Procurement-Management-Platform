from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    current_quantity: float
    alert_type: str
    is_acknowledged: bool
    created_at: datetime
    acknowledged_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    total: int
    page: int
    page_size: int
    total_pages: int