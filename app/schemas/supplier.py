from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class SupplierCreate(BaseModel):
    supplier_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    contact_person: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    phone: str = Field(
        ...,
        min_length=10,
        max_length=20
    )

    gst_number: str = Field(
        ...,
        min_length=15,
        max_length=15
    )

    address: str = Field(
        ...,
        min_length=3,
        max_length=255
    )

    rating: float = Field(
        default=0,
        ge=0,
        le=5
    )

    @field_validator("gst_number")
    @classmethod
    def validate_gst_number(cls, value: str):
        value = value.upper()

        if len(value) != 15:
            raise ValueError(
                "GST number must contain exactly 15 characters"
            )

        return value


class SupplierUpdate(BaseModel):
    supplier_name: str | None = Field(
        None,
        min_length=2,
        max_length=150
    )

    contact_person: str | None = Field(
        None,
        min_length=2,
        max_length=100
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        None,
        min_length=10,
        max_length=20
    )

    gst_number: str | None = Field(
        None,
        min_length=15,
        max_length=15
    )

    address: str | None = Field(
        None,
        min_length=3,
        max_length=255
    )

    rating: float | None = Field(
        None,
        ge=0,
        le=5
    )

    @field_validator("gst_number")
    @classmethod
    def validate_gst_number(cls, value: str | None):
        if value is None:
            return value

        return value.upper()


class SupplierResponse(BaseModel):
    id: int
    supplier_name: str
    contact_person: str
    email: EmailStr
    phone: str
    gst_number: str
    address: str
    rating: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SupplierListResponse(BaseModel):
    items: list[SupplierResponse]
    total: int
    page: int
    page_size: int
    total_pages: int