from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "warehouse_id",
            name="uq_inventory_product_warehouse"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey(
            "products.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    warehouse_id = Column(
        Integer,
        ForeignKey(
            "warehouses.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    available_quantity = Column(
        Float,
        nullable=False,
        default=0
    )

    reserved_quantity = Column(
        Float,
        nullable=False,
        default=0
    )

    damaged_quantity = Column(
        Float,
        nullable=False,
        default=0
    )

    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    product = relationship(
        "Product"
    )

    warehouse = relationship(
        "Warehouse"
    )