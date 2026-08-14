from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ProductCreate(BaseModel):

    sku: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    product_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    category_id: int = Field(
        ...,
        gt=0
    )

    brand: str | None = Field(
        None,
        max_length=100
    )

    unit: str = Field(
        ...,
        min_length=1,
        max_length=30
    )

    cost_price: float = Field(
        ...,
        ge=0
    )

    selling_price: float = Field(
        ...,
        ge=0
    )

    reorder_level: float = Field(
        ...,
        ge=0
    )

    barcode: str | None = Field(
        None,
        max_length=100
    )


class ProductUpdate(BaseModel):

    sku: str | None = Field(
        None,
        min_length=2,
        max_length=50
    )

    product_name: str | None = Field(
        None,
        min_length=2,
        max_length=150
    )

    category_id: int | None = Field(
        None,
        gt=0
    )

    brand: str | None = Field(
        None,
        max_length=100
    )

    unit: str | None = Field(
        None,
        min_length=1,
        max_length=30
    )

    cost_price: float | None = Field(
        None,
        ge=0
    )

    selling_price: float | None = Field(
        None,
        ge=0
    )

    reorder_level: float | None = Field(
        None,
        ge=0
    )

    barcode: str | None = Field(
        None,
        max_length=100
    )


class ProductResponse(BaseModel):

    id: int
    sku: str
    product_name: str
    category_id: int
    brand: str | None
    unit: str
    cost_price: float
    selling_price: float
    reorder_level: float
    barcode: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ProductListResponse(BaseModel):

    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int