from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.sql import func

from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    supplier_name = Column(
        String(150),
        nullable=False,
        index=True
    )

    contact_person = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True
    )

    phone = Column(
        String(20),
        nullable=False
    )

    gst_number = Column(
        String(15),
        nullable=False,
        unique=True,
        index=True
    )

    address = Column(
        String(255),
        nullable=False
    )

    rating = Column(
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