from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    # =========================================================
    # CREATE
    # =========================================================

    @staticmethod
    def create(
        db: Session,
        user: User
    ):
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    # =========================================================
    # GET BY ID
    # =========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int
    ):
        return (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

    # =========================================================
    # GET BY EMAIL
    # =========================================================

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ):
        return (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

    # =========================================================
    # GET BY ID WITH ROLE
    # =========================================================

    @staticmethod
    def get_by_id_with_role(
        db: Session,
        user_id: int
    ):
        return (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

    # =========================================================
    # GET ALL
    # =========================================================

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int
    ):
        query = (
            db.query(User)
            .order_by(
                User.id.desc()
            )
        )

        total = query.count()

        offset = (
            (page - 1)
            * page_size
        )

        users = (
            query
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return users, total

    # =========================================================
    # UPDATE
    # =========================================================

    @staticmethod
    def update(
        db: Session,
        user: User
    ):
        db.commit()
        db.refresh(user)

        return user

    # =========================================================
    # DELETE
    # =========================================================

    @staticmethod
    def delete(
        db: Session,
        user: User
    ):
        db.delete(user)
        db.commit()

    # =========================================================
    # EMAIL EXISTS
    # =========================================================

    @staticmethod
    def email_exists(
        db: Session,
        email: str,
        exclude_user_id: int | None = None
    ):
        query = (
            db.query(User)
            .filter(
                User.email == email
            )
        )

        if exclude_user_id is not None:
            query = query.filter(
                User.id != exclude_user_id
            )

        return (
            query.first()
            is not None
        )