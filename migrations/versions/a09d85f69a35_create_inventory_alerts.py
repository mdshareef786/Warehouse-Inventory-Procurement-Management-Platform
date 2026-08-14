"""Create inventory alerts

Revision ID: a09d85f69a35
Revises: af8829057863
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a09d85f69a35"
down_revision: Union[str, Sequence[str], None] = "af8829057863"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inventory_alerts",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey(
                "products.id",
                ondelete="CASCADE"
            ),
            nullable=False
        ),

        sa.Column(
            "warehouse_id",
            sa.Integer(),
            sa.ForeignKey(
                "warehouses.id",
                ondelete="CASCADE"
            ),
            nullable=False
        ),

        sa.Column(
            "current_quantity",
            sa.Float(),
            nullable=False
        ),

        sa.Column(
            "alert_type",
            sa.String(length=50),
            nullable=False
        ),

        sa.Column(
            "is_acknowledged",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),

        sa.Column(
            "acknowledged_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),
    )

    op.create_index(
        "ix_inventory_alerts_product_id",
        "inventory_alerts",
        ["product_id"]
    )

    op.create_index(
        "ix_inventory_alerts_warehouse_id",
        "inventory_alerts",
        ["warehouse_id"]
    )

    op.create_index(
        "ix_inventory_alerts_alert_type",
        "inventory_alerts",
        ["alert_type"]
    )

    op.create_index(
        "ix_inventory_alerts_created_at",
        "inventory_alerts",
        ["created_at"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_inventory_alerts_created_at",
        table_name="inventory_alerts"
    )

    op.drop_index(
        "ix_inventory_alerts_alert_type",
        table_name="inventory_alerts"
    )

    op.drop_index(
        "ix_inventory_alerts_warehouse_id",
        table_name="inventory_alerts"
    )

    op.drop_index(
        "ix_inventory_alerts_product_id",
        table_name="inventory_alerts"
    )

    op.drop_table("inventory_alerts")