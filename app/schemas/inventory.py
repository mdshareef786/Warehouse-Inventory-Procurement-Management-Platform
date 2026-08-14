from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class StockInRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    warehouse_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    reason: str | None = Field(
        None,
        max_length=255
    )


class StockOutRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    warehouse_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    reason: str | None = Field(
        None,
        max_length=255
    )


class InventoryAdjustRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    warehouse_id: int = Field(..., gt=0)
    quantity: float = Field(..., ge=0)
    reason: str = Field(
        ...,
        min_length=3,
        max_length=255
    )


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    available_quantity: float
    reserved_quantity: float
    damaged_quantity: float
    last_updated: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class InventoryTransactionResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    transaction_type: str
    quantity: float
    previous_quantity: float
    new_quantity: float
    reference_type: str | None
    reference_id: int | None
    reason: str | None
    performed_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class InventoryListResponse(BaseModel):
    items: list[InventoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class InventoryTransactionListResponse(BaseModel):
    items: list[InventoryTransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class InventoryReserveRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    warehouse_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    reason: str | None = Field(
        None,
        max_length=255
    )


class InventoryReleaseRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    warehouse_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    reason: str | None = Field(
        None,
        max_length=255
    )

class InventoryDamageRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    warehouse_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    reason: str = Field(
        ...,
        min_length=3,
        max_length=255
    )

class InventoryReconciliationRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    warehouse_id: int = Field(..., gt=0)
    physical_quantity: float = Field(..., ge=0)
    reason: str = Field(
        ...,
        min_length=3,
        max_length=255
    )