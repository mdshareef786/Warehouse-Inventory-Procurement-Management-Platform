from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GoodsReceiptItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)


class GoodsReceiptCreate(BaseModel):
    purchase_order_id: int = Field(..., gt=0)

    items: list[GoodsReceiptItemCreate] = Field(
        ...,
        min_length=1,
    )


class GoodsReceiptItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: float

    model_config = ConfigDict(
        from_attributes=True
    )


class GoodsReceiptResponse(BaseModel):
    id: int
    receipt_number: str
    purchase_order_id: int
    warehouse_id: int
    received_by: int
    total_quantity: float
    status: str
    received_at: datetime
    created_at: datetime

    items: list[GoodsReceiptItemResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


class GoodsReceiptListResponse(BaseModel):
    items: list[GoodsReceiptResponse]
    total: int
    page: int
    page_size: int
    total_pages: int