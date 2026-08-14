from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class PurchaseOrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)

    quantity: float = Field(
        ...,
        gt=0
    )

    unit_price: float = Field(
        ...,
        ge=0
    )


class PurchaseOrderCreate(BaseModel):

    supplier_id: int = Field(
        ...,
        gt=0
    )

    warehouse_id: int = Field(
        ...,
        gt=0
    )

    expected_delivery_date: datetime | None = None

    items: list[PurchaseOrderItemCreate] = Field(
        ...,
        min_length=1
    )


class PurchaseOrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    received_quantity: float
    unit_price: float
    total_price: float

    model_config = ConfigDict(
        from_attributes=True
    )


class PurchaseOrderResponse(BaseModel):

    id: int
    po_number: str
    supplier_id: int
    warehouse_id: int
    order_date: datetime
    expected_delivery_date: datetime | None
    status: str
    total_amount: float
    created_by: int
    approved_by: int | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    items: list[PurchaseOrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


class PurchaseOrderListResponse(BaseModel):
    items: list[PurchaseOrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PurchaseOrderReceiveItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)


class PurchaseOrderReceiveRequest(BaseModel):
    items: list[PurchaseOrderReceiveItem] = Field(
        ...,
        min_length=1
    )