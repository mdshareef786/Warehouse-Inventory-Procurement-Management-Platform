import math

from sqlalchemy.orm import Session

from app.models.user import User

from app.repositories.user_repository import (
    UserRepository
)

from app.repositories.role_repository import (
    RoleRepository
)

from app.models.warehouse import Warehouse

from app.exceptions.custom_exceptions import (
    UserNotFoundException,
)


class UserService:

    # =========================================================
    # GET ALL USERS
    # =========================================================

    @staticmethod
    def get_all(
        db: Session,
        page: int,
        page_size: int
    ):

        users, total = (
            UserRepository.get_all(
                db=db,
                page=page,
                page_size=page_size
            )
        )

        total_pages = (
            math.ceil(
                total / page_size
            )
            if total
            else 0
        )

        return {
            "items": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    # =========================================================
    # GET USER
    # =========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int
    ):

        user = (
            UserRepository.get_by_id(
                db,
                user_id
            )
        )

        if not user:
            raise UserNotFoundException(
                "User not found"
            )

        return user

    # =========================================================
    # UPDATE USER
    # =========================================================

    @staticmethod
    def update(
        db: Session,
        user_id: int,
        data
    ):

        user = (
            UserService.get_by_id(
                db,
                user_id
            )
        )

        # -----------------------------------------------------
        # FULL NAME
        # -----------------------------------------------------

        if data.full_name is not None:
            user.full_name = data.full_name

        # -----------------------------------------------------
        # EMAIL
        # -----------------------------------------------------

        if data.email is not None:

            email = str(data.email).lower()

            if (
                email != user.email
                and UserRepository.email_exists(
                    db,
                    email,
                    exclude_user_id=user.id
                )
            ):
                raise ValueError(
                    "Email already exists"
                )

            user.email = email

        # -----------------------------------------------------
        # ROLE
        # -----------------------------------------------------

        if data.role_id is not None:

            role = (
                RoleRepository.get_by_id(
                    db,
                    data.role_id
                )
            )

            if not role:
                raise ValueError(
                    "Role not found"
                )

            user.role_id = data.role_id

        # -----------------------------------------------------
        # WAREHOUSE
        # -----------------------------------------------------

        if data.warehouse_id is not None:

            warehouse = (
                db.query(Warehouse)
                .filter(
                    Warehouse.id
                    == data.warehouse_id
                )
                .first()
            )

            if not warehouse:
                raise ValueError(
                    "Warehouse not found"
                )

            if warehouse.status != "ACTIVE":
                raise ValueError(
                    "Warehouse is not active"
                )

            user.warehouse_id = (
                data.warehouse_id
            )

        return UserRepository.update(
            db,
            user
        )

    # =========================================================
    # UPDATE STATUS
    # =========================================================

    @staticmethod
    def update_status(
        db: Session,
        user_id: int,
        is_active: bool
    ):

        user = (
            UserService.get_by_id(
                db,
                user_id
            )
        )

        user.is_active = is_active

        return UserRepository.update(
            db,
            user
        )

    # =========================================================
    # DELETE USER
    # =========================================================

    @staticmethod
    def delete(
        db: Session,
        user_id: int
    ):

        user = (
            UserService.get_by_id(
                db,
                user_id
            )
        )

        UserRepository.delete(
            db,
            user
        )

        return {
            "message": "User deleted successfully"
        }