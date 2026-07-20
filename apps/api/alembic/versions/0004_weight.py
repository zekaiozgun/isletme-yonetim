"""Weight module: weighing_methods, weight_records

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "weighing_methods",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code", name="uq_weighing_methods_code"),
        sa.UniqueConstraint("name", name="uq_weighing_methods_name"),
    )

    op.create_table(
        "weight_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("animal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("weigh_date", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(6, 2), nullable=False),
        sa.Column("weighing_method_id", sa.Integer(), sa.ForeignKey("weighing_methods.id"), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_weight_records_animal_id", "weight_records", ["animal_id"])


def downgrade() -> None:
    op.drop_index("ix_weight_records_animal_id", table_name="weight_records")
    op.drop_table("weight_records")
    op.drop_table("weighing_methods")
