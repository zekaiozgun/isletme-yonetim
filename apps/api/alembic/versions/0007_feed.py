"""Feed module: feed_types, feed_units, feed_items, feed_distributions

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LOOKUP_TABLES = ["feed_types", "feed_units"]


def _create_lookup_table(name: str) -> None:
    op.create_table(
        name,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code", name=f"uq_{name}_code"),
        sa.UniqueConstraint("name", name=f"uq_{name}_name"),
    )


def upgrade() -> None:
    for table_name in LOOKUP_TABLES:
        _create_lookup_table(table_name)

    op.create_table(
        "feed_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("feed_type_id", sa.Integer(), sa.ForeignKey("feed_types.id"), nullable=False),
        sa.Column("default_unit_id", sa.Integer(), sa.ForeignKey("feed_units.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_feed_items_name"),
    )

    op.create_table(
        "feed_distributions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("pen_id", sa.Integer(), sa.ForeignKey("pens.id"), nullable=False),
        sa.Column("feed_item_id", sa.Integer(), sa.ForeignKey("feed_items.id"), nullable=False),
        sa.Column("distribution_date", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(8, 2), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("feed_units.id"), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_feed_distributions_pen_id", "feed_distributions", ["pen_id"])


def downgrade() -> None:
    op.drop_index("ix_feed_distributions_pen_id", table_name="feed_distributions")
    op.drop_table("feed_distributions")
    op.drop_table("feed_items")

    for table_name in reversed(LOOKUP_TABLES):
        op.drop_table(table_name)
