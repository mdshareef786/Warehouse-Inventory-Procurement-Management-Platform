from sqlalchemy.orm import Session

from app.models.role import Role


class RoleRepository:

    @staticmethod
    def get_by_name(db: Session, name: str):
        return (
            db.query(Role)
            .filter(Role.name == name)
            .first()
        )

    @staticmethod
    def get_by_id(db: Session, role_id: int):
        return (
            db.query(Role)
            .filter(Role.id == role_id)
            .first()
        )

    @staticmethod
    def get_all(db: Session):
        return db.query(Role).all()