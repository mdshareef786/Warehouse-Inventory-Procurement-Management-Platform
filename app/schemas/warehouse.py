from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class WarehouseCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    address: str = Field(..., min_length=3, max_length=255)
    capacity: float = Field(..., gt=0)


class WarehouseUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    address: str | None = Field(None, min_length=3, max_length=255)
    capacity: float | None = Field(None, gt=0)


class WarehouseManagerAssign(BaseModel):
    manager_id: int = Field(..., gt=0)


class WarehouseResponse(BaseModel):
    id: int
    name: str
    code: str
    address: str
    capacity: float
    current_utilization: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseListResponse(BaseModel):
    items: list[WarehouseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int