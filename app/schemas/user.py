from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role_id: int
    warehouse_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(
        None,
        min_length=3,
        max_length=100
    )

    email: EmailStr | None = None

    role_id: int | None = Field(
        None,
        gt=0
    )

    warehouse_id: int | None = Field(
        None,
        gt=0
    )


class UserStatusUpdateRequest(BaseModel):
    is_active: bool