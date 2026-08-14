from datetime import datetime, timedelta
import secrets

from app.core.logger import logger
from app.models.password_reset import PasswordResetToken
from app.repositories.password_reset_repository import (
    PasswordResetRepository
)
from app.exceptions.custom_exceptions import (
    UserNotFoundException,
    PasswordResetTokenInvalidException,
    PasswordResetTokenExpiredException,
)
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.auth_repository import AuthRepository
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from datetime import datetime, timedelta, timezone

from app.exceptions.custom_exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    RoleNotFoundException,
    InvalidRefreshTokenException,
    RefreshTokenExpiredException,
)


class AuthService:

    @staticmethod
    def register(db: Session, data):

        role = RoleRepository.get_by_name(
            db,
            "INVENTORY_STAFF"
        )

        if not role:
            raise Exception("Default role not found")

        user = User(
            full_name=data.full_name,
            email=data.email,
            password=hash_password(data.password),
            role_id=role.id
        )
        return UserRepository.create(db, user)

    @staticmethod
    def login(db: Session, data):

        user = UserRepository.get_by_email(
            db,
            data.email
        )

        if not user:
            raise Exception("Invalid credentials")

        if not verify_password(
                data.password,
                user.password):
            raise Exception("Invalid credentials")

        access = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.name
            }
        )

        refresh = create_refresh_token(
            {
                "sub": str(user.id)
            }
        )

        refresh_obj = RefreshToken(
            token=refresh,
            expires_at=datetime.utcnow() + timedelta(days=7),
            user_id=user.id
        )

        AuthRepository.save_refresh_token(
            db,
            refresh_obj
        )

        return {
            "access_token": access,
            "refresh_token": refresh
        }

    @staticmethod
    def refresh_access_token(
        db: Session,
        refresh_token: str
    ):

        token_record = AuthRepository.get_refresh_token(
            db,
            refresh_token
        )

        if not token_record:
            raise InvalidRefreshTokenException(
                "Invalid or revoked refresh token"
            )

        if token_record.expires_at <= datetime.now(timezone.utc):
            raise RefreshTokenExpiredException(
                "Refresh token has expired"
            )

        user = UserRepository.get_by_id(
            db,
            token_record.user_id
        )

        if not user:
            raise InvalidRefreshTokenException(
                "User associated with token was not found"
            )

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.name
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    @staticmethod
    def logout(
        db: Session,
        refresh_token: str
    ):

        token_record = AuthRepository.get_refresh_token(
            db,
            refresh_token
        )

        if not token_record:
            raise InvalidRefreshTokenException(
                "Invalid or already revoked refresh token"
            )

        AuthRepository.revoke_refresh_token(
            db,
            token_record
        )

        return {
            "message": "Logged out successfully"
        }

    @staticmethod
    def forgot_password(
        db: Session,
        email: str
    ):

        user = UserRepository.get_by_email(
            db,
            email
        )

        # Do not reveal whether an email exists.
        if not user:
            return {
                "message": "If the email exists, a password reset link will be generated."
            }

        raw_token = secrets.token_urlsafe(32)

        reset_token = PasswordResetToken(
            token=raw_token,
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(minutes=15)
            ),
            user_id=user.id
        )

        PasswordResetRepository.create(
            db,
            reset_token
        )

        logger.info(
            f"Password reset requested for user_id={user.id}"
        )

        # Development only.
        # Later we'll send this through email.
        return {
            "message": "Password reset token generated.",
            "reset_token": raw_token
        }

    @staticmethod
    def reset_password(
        db: Session,
        token: str,
        new_password: str
    ):

        reset_token = (
            PasswordResetRepository.get_valid_token(
                db,
                token
            )
        )

        if not reset_token:
            raise PasswordResetTokenInvalidException(
                "Invalid or already used password reset token"
            )

        if reset_token.expires_at <= datetime.now(timezone.utc):
            raise PasswordResetTokenExpiredException(
                "Password reset token has expired"
            )

        user = UserRepository.get_by_id(
            db,
            reset_token.user_id
        )

        if not user:
            raise UserNotFoundException(
                "User not found"
            )

        user.password = hash_password(
            new_password
        )

        PasswordResetRepository.mark_used(
            db,
            reset_token
        )

        AuthRepository.revoke_all_user_tokens(
            db,
            user.id
        )

        db.commit()

        logger.info(
            f"Password reset completed for user_id={user.id}"
        )

        return {
            "message": "Password reset successfully"
        }