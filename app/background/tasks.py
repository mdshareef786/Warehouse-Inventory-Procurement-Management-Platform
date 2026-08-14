from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logger import logger
from app.models.refresh_token import RefreshToken


def cleanup_expired_refresh_tokens():
    """
    Remove expired refresh tokens from the database.
    """

    db: Session = SessionLocal()

    try:
        now = datetime.now(timezone.utc)

        deleted = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.expires_at < now
            )
            .delete(
                synchronize_session=False
            )
        )

        db.commit()

        logger.info(
            f"Background cleanup: deleted {deleted} expired refresh tokens"
        )

        return deleted

    except Exception:
        db.rollback()

        logger.exception(
            "Background refresh-token cleanup failed"
        )

        return 0

    finally:
        db.close()