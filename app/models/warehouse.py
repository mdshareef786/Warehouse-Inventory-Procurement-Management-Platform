from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    address = Column(
        String(255),
        nullable=False
    )

    capacity = Column(
        Float,
        nullable=False
    )

    current_utilization = Column(
        Float,
        default=0,
        nullable=False
    )

    status = Column(
        String(20),
        default="ACTIVE",
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    employees = relationship(
        "User",
        back_populates="warehouse",
        foreign_keys="User.warehouse_id"
    )