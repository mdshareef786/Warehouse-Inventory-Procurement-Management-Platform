from sqlalchemy import (
    Boolean,
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

class InventoryAlert(Base):
    __tablename__ = "inventory_alerts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey(
            "products.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    warehouse_id = Column(
        Integer,
        ForeignKey(
            "warehouses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    current_quantity = Column(
        Float,
        nullable=False,
    )

    alert_type = Column(
        String(30),
        nullable=False,
        index=True,
    )

    is_acknowledged = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    acknowledged_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    product = relationship("Product")
    warehouse = relationship("Warehouse")