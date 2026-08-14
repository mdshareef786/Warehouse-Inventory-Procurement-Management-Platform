from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sku = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    product_name = Column(
        String(150),
        nullable=False,
        index=True
    )

    category_id = Column(
        Integer,
        ForeignKey(
            "categories.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    brand = Column(
        String(100),
        nullable=True
    )

    unit = Column(
        String(30),
        nullable=False
    )

    cost_price = Column(
        Float,
        nullable=False
    )

    selling_price = Column(
        Float,
        nullable=False
    )

    reorder_level = Column(
        Float,
        nullable=False,
        default=0
    )

    barcode = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="ACTIVE",
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

    category = relationship(
        "Category",
        back_populates="products"
    )