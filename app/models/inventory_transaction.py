from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

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

    transaction_type = Column(
        String(30),
        nullable=False,
        index=True
    )

    quantity = Column(
        Float,
        nullable=False
    )

    previous_quantity = Column(
        Float,
        nullable=False
    )

    new_quantity = Column(
        Float,
        nullable=False
    )

    reference_type = Column(
        String(50),
        nullable=True
    )

    reference_id = Column(
        Integer,
        nullable=True
    )

    reason = Column(
        Text,
        nullable=True
    )

    performed_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    product = relationship(
        "Product"
    )

    warehouse = relationship(
        "Warehouse"
    )

    user = relationship(
        "User"
    )