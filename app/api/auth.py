from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    UserRegister,
    UserLogin,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    RefreshTokenRequest,
    LogoutRequest,
)

from app.schemas.auth import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    try:
        return AuthService.register(
            db,
            data
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
def login(
    data: UserLogin,
    db: Session = Depends(get_db)
):
    try:
        return AuthService.login(
            db,
            data
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user=Depends(get_current_user)
):
    return current_user

@router.post("/refresh")
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    return AuthService.refresh_access_token(
        db,
        data.refresh_token
    )

@router.post("/logout")
def logout(
    data: LogoutRequest,
    db: Session = Depends(get_db)
):
    return AuthService.logout(
        db,
        data.refresh_token
    )

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    return AuthService.forgot_password(
        db,
        data.email
    )

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    return AuthService.reset_password(
        db,
        data.token,
        data.new_password
    )