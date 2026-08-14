from sqlalchemy.orm import Session

from app.models.password_reset import PasswordResetToken


class PasswordResetRepository:

    @staticmethod
    def create(
        db: Session,
        reset_token: PasswordResetToken
    ):
        db.add(reset_token)
        db.commit()
        db.refresh(reset_token)

        return reset_token

    @staticmethod
    def get_valid_token(
        db: Session,
        token: str
    ):
        return (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token == token,
                PasswordResetToken.is_used.is_(False)
            )
            .first()
        )

    @staticmethod
    def mark_used(
        db: Session,
        reset_token: PasswordResetToken
    ):
        reset_token.is_used = True

        db.commit()
        db.refresh(reset_token)

        return reset_token