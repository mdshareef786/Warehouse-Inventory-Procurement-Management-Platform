from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class AuthRepository:

    @staticmethod
    def save_refresh_token(
        db: Session,
        token: RefreshToken
    ):
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    @staticmethod
    def get_refresh_token(
        db: Session,
        token: str
    ):
        return (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token == token,
                RefreshToken.revoked.is_(False)
            )
            .first()
        )

    @staticmethod
    def revoke_refresh_token(
        db: Session,
        refresh_token: RefreshToken
    ):
        refresh_token.revoked = True
        db.commit()
        db.refresh(refresh_token)

        return refresh_token

    @staticmethod
    def revoke_all_user_tokens(
        db: Session,
        user_id: int
    ):
        (
            db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False)
            )
            .update(
                {
                    RefreshToken.revoked: True
                },
                synchronize_session=False
            )
        )

        db.commit()