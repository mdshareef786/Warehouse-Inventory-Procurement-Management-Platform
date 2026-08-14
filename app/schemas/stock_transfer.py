from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# =========================================================
# CREATE TRANSFER
# =========================================================

class StockTransferItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)

    quantity: float = Field(
        ...,
        gt=0
    )


class StockTransferCreate(BaseModel):
    source_warehouse_id: int = Field(
        ...,
        gt=0
    )

    destination_warehouse_id: int = Field(
        ...,
        gt=0
    )

    items: list[StockTransferItemCreate] = Field(
        ...,
        min_length=1
    )


# =========================================================
# RESPONSE
# =========================================================

class StockTransferItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    received_quantity: float

    model_config = ConfigDict(
        from_attributes=True
    )


class StockTransferResponse(BaseModel):
    id: int
    transfer_number: str

    source_warehouse_id: int
    destination_warehouse_id: int

    requested_by: int
    approved_by: int | None

    status: str

    requested_at: datetime
    approved_at: datetime | None
    received_at: datetime | None

    created_at: datetime
    updated_at: datetime

    items: list[StockTransferItemResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# LIST RESPONSE
# =========================================================

class StockTransferListResponse(BaseModel):
    items: list[StockTransferResponse]

    total: int
    page: int
    page_size: int
    total_pages: int