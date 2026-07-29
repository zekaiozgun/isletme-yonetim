"""Feed V2: gunluk dagitim kaydini rasyon donemi + alim (stok) modeliyle degistir

feed_distributions uretimde bos (0 satir) - guvenle kaldiriliyor.

Revision ID: 0020
Revises: 0019
Create Date: 2026-07-29

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0020"
down_revision: Union[str, None] = "0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_feed_distributions_pen_id", table_name="feed_distributions")
    op.drop_table("feed_distributions")

    op.create_table(
        "feed_purchases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("feed_item_id", sa.Integer(), sa.ForeignKey("feed_items.id"), nullable=False),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("feed_units.id"), nullable=False),
        sa.Column("total_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_feed_purchases_feed_item_id", "feed_purchases", ["feed_item_id"])

    op.create_table(
        "pen_rations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("pen_id", sa.Integer(), sa.ForeignKey("pens.id"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_pen_rations_pen_id", "pen_rations", ["pen_id"])

    op.create_table(
        "ration_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ration_id", sa.Integer(), sa.ForeignKey("pen_rations.id"), nullable=False),
        sa.Column("feed_item_id", sa.Integer(), sa.ForeignKey("feed_items.id"), nullable=False),
        sa.Column("daily_quantity_per_animal", sa.Numeric(8, 3), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("feed_units.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_ration_items_ration_id", "ration_items", ["ration_id"])


def downgrade() -> None:
    op.drop_index("ix_ration_items_ration_id", table_name="ration_items")
    op.drop_table("ration_items")

    op.drop_index("ix_pen_rations_pen_id", table_name="pen_rations")
    op.drop_table("pen_rations")

    op.drop_index("ix_feed_purchases_feed_item_id", table_name="feed_purchases")
    op.drop_table("feed_purchases")

    op.create_table(
        "feed_distributions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("pen_id", sa.Integer(), sa.ForeignKey("pens.id"), nullable=False),
        sa.Column("feed_item_id", sa.Integer(), sa.ForeignKey("feed_items.id"), nullable=False),
        sa.Column("distribution_date", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(8, 2), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("feed_units.id"), nullable=False),
        sa.Column("total_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_feed_distributions_pen_id", "feed_distributions", ["pen_id"])
