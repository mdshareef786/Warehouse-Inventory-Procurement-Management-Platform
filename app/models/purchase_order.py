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


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    po_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    supplier_id = Column(
        Integer,
        ForeignKey(
            "suppliers.id",
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

    order_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    expected_delivery_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="DRAFT",
        index=True
    )

    total_amount = Column(
        Float,
        nullable=False,
        default=0
    )

    created_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    approved_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT"
        ),
        nullable=True
    )

    approved_at = Column(
        DateTime(timezone=True),
        nullable=True
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

    supplier = relationship(
        "Supplier"
    )

    warehouse = relationship(
        "Warehouse"
    )

    items = relationship(
        "PurchaseOrderItem",
        back_populates="purchase_order",
        cascade="all, delete-orphan"
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by]
    )

    approver = relationship(
        "User",
        foreign_keys=[approved_by]
    )


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    purchase_order_id = Column(
        Integer,
        ForeignKey(
            "purchase_orders.id",
            ondelete="CASCADE"
        ),
        nullable=False,
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

    quantity = Column(
        Float,
        nullable=False
    )

    received_quantity = Column(
        Float,
        nullable=False,
        default=0
    )

    unit_price = Column(
        Float,
        nullable=False
    )

    total_price = Column(
        Float,
        nullable=False
    )

    purchase_order = relationship(
        "PurchaseOrder",
        back_populates="items"
    )

    product = relationship(
        "Product"
    )