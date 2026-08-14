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


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    receipt_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    purchase_order_id = Column(
        Integer,
        ForeignKey(
            "purchase_orders.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    warehouse_id = Column(
        Integer,
        ForeignKey(
            "warehouses.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    received_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    total_quantity = Column(
        Float,
        nullable=False,
        default=0,
    )

    status = Column(
        String(20),
        nullable=False,
        default="RECEIVED",
        index=True,
    )

    received_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    purchase_order = relationship(
        "PurchaseOrder",
    )

    warehouse = relationship(
        "Warehouse",
    )

    user = relationship(
        "User",
    )

    items = relationship(
        "GoodsReceiptItem",
        back_populates="goods_receipt",
        cascade="all, delete-orphan",
    )


class GoodsReceiptItem(Base):
    __tablename__ = "goods_receipt_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    goods_receipt_id = Column(
        Integer,
        ForeignKey(
            "goods_receipts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey(
            "products.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    quantity = Column(
        Float,
        nullable=False,
    )

    goods_receipt = relationship(
        "GoodsReceipt",
        back_populates="items",
    )

    product = relationship(
        "Product",
    )