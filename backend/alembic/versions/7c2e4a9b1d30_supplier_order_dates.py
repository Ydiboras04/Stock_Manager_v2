"""supplier order dates

Revision ID: 7c2e4a9b1d30
Revises: 581461780e16
Create Date: 2026-10-16 13:30:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7c2e4a9b1d30"
down_revision: str | None = "581461780e16"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Existing orders get the migration time as their creation date.
    op.add_column(
        "supplier_orders",
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.alter_column("supplier_orders", "created_at", server_default=None)
    # Unknown for existing orders, so left empty.
    op.add_column("supplier_orders", sa.Column("shipped_at", sa.DateTime(timezone=True)))
    op.add_column("supplier_orders", sa.Column("received_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("supplier_orders", "received_at")
    op.drop_column("supplier_orders", "shipped_at")
    op.drop_column("supplier_orders", "created_at")
