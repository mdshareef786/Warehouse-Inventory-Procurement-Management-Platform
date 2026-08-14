from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.dependencies.auth import require_roles

from app.schemas.user import (
    UserResponse,
    UserListResponse,
    UserUpdateRequest,
    UserStatusUpdateRequest,
)

from app.services.user_service import (
    UserService
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================================================
# GET ALL USERS
# =========================================================

@router.get(
    "",
    response_model=UserListResponse
)
def get_users(
    page: int = Query(
        1,
        ge=1
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN"
        )
    )
):

    return UserService.get_all(
        db=db,
        page=page,
        page_size=page_size
    )


# =========================================================
# GET USER BY ID
# =========================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN"
        )
    )
):

    return UserService.get_by_id(
        db=db,
        user_id=user_id
    )


# =========================================================
# UPDATE USER
# =========================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN"
        )
    )
):

    return UserService.update(
        db=db,
        user_id=user_id,
        data=data
    )


# =========================================================
# ACTIVATE / DEACTIVATE USER
# =========================================================

@router.patch(
    "/{user_id}/status",
    response_model=UserResponse
)
def update_user_status(
    user_id: int,
    data: UserStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN"
        )
    )
):

    return UserService.update_status(
        db=db,
        user_id=user_id,
        is_active=data.is_active
    )


# =========================================================
# DELETE USER
# =========================================================

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "SUPER_ADMIN"
        )
    )
):

    UserService.delete(
        db=db,
        user_id=user_id
    )

    return None