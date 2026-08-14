"""sync inventory alert and stock transfer indexes

Revision ID: f144815caf89
Revises: a09d85f69a35
Create Date: 2026-08-13 15:07:51.417997

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f144815caf89"
down_revision: Union[str, Sequence[str], None] = "a09d85f69a35"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Change alert_type from VARCHAR(50) to VARCHAR(30)
    op.alter_column(
        "inventory_alerts",
        "alert_type",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=30),
        existing_nullable=False,
    )

    # The old created_at index does not exist in the actual database,
    # so we intentionally do NOT drop it here.

    # Add missing indexes
    op.create_index(
        op.f("ix_inventory_alerts_id"),
        "inventory_alerts",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_inventory_alerts_is_acknowledged"),
        "inventory_alerts",
        ["is_acknowledged"],
        unique=False,
    )

    op.create_index(
        op.f("ix_stock_transfer_items_product_id"),
        "stock_transfer_items",
        ["product_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_stock_transfer_items_transfer_id"),
        "stock_transfer_items",
        ["transfer_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_stock_transfers_destination_warehouse_id"),
        "stock_transfers",
        ["destination_warehouse_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_stock_transfers_source_warehouse_id"),
        "stock_transfers",
        ["source_warehouse_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_stock_transfers_source_warehouse_id"),
        table_name="stock_transfers",
    )

    op.drop_index(
        op.f("ix_stock_transfers_destination_warehouse_id"),
        table_name="stock_transfers",
    )

    op.drop_index(
        op.f("ix_stock_transfer_items_transfer_id"),
        table_name="stock_transfer_items",
    )

    op.drop_index(
        op.f("ix_stock_transfer_items_product_id"),
        table_name="stock_transfer_items",
    )

    op.drop_index(
        op.f("ix_inventory_alerts_is_acknowledged"),
        table_name="inventory_alerts",
    )

    op.drop_index(
        op.f("ix_inventory_alerts_id"),
        table_name="inventory_alerts",
    )

    # Do NOT recreate ix_inventory_alerts_created_at because
    # it does not exist in the actual database.

    op.alter_column(
        "inventory_alerts",
        "alert_type",
        existing_type=sa.String(length=30),
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
    )