"""dates and notifications

Revision ID: 581461780e16
Revises: a20bb93841d6
Create Date: 2026-10-16 12:34:57.942666

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "581461780e16"
down_revision: str | None = "a20bb93841d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipient", sa.String(length=30), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_recipient"), "notifications", ["recipient"])

    # Existing rows get the migration time as their date.
    for table in ("customer_orders", "purchase_requests"):
        op.add_column(
            table,
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )
        op.alter_column(table, "created_at", server_default=None)

    # Out-of-stock customer orders are now rejected automatically.
    op.execute("UPDATE customer_orders SET status = 'REJECTED' WHERE status = 'OUT_OF_STOCK'")


def downgrade() -> None:
    op.execute("UPDATE customer_orders SET status = 'OUT_OF_STOCK' WHERE status = 'REJECTED'")
    op.drop_column("purchase_requests", "created_at")
    op.drop_column("customer_orders", "created_at")
    op.drop_index(op.f("ix_notifications_recipient"), table_name="notifications")
    op.drop_table("notifications")
