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


class StockTransfer(Base):
    __tablename__ = "stock_transfers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    transfer_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    source_warehouse_id = Column(
        Integer,
        ForeignKey(
            "warehouses.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    destination_warehouse_id = Column(
        Integer,
        ForeignKey(
            "warehouses.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    requested_by = Column(
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

    status = Column(
        String(30),
        nullable=False,
        default="REQUESTED",
        index=True
    )

    requested_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    approved_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    received_at = Column(
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

    source_warehouse = relationship(
        "Warehouse",
        foreign_keys=[source_warehouse_id]
    )

    destination_warehouse = relationship(
        "Warehouse",
        foreign_keys=[destination_warehouse_id]
    )

    requester = relationship(
        "User",
        foreign_keys=[requested_by]
    )

    approver = relationship(
        "User",
        foreign_keys=[approved_by]
    )

    items = relationship(
        "StockTransferItem",
        back_populates="transfer",
        cascade="all, delete-orphan"
    )


class StockTransferItem(Base):
    __tablename__ = "stock_transfer_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    transfer_id = Column(
        Integer,
        ForeignKey(
            "stock_transfers.id",
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

    transfer = relationship(
        "StockTransfer",
        back_populates="items"
    )

    product = relationship(
        "Product"
    )