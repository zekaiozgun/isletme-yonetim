"""Pen module: pen_types, pen_assignment_reasons, pens, pen_assignments

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LOOKUP_TABLES = ["pen_types", "pen_assignment_reasons"]


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
        "pens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("pen_type_id", sa.Integer(), sa.ForeignKey("pen_types.id"), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code", name="uq_pens_code"),
    )

    op.create_table(
        "pen_assignments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("animal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("pen_id", sa.Integer(), sa.ForeignKey("pens.id"), nullable=False),
        sa.Column("assigned_date", sa.Date(), nullable=False),
        sa.Column("removed_date", sa.Date(), nullable=True),
        sa.Column("reason_id", sa.Integer(), sa.ForeignKey("pen_assignment_reasons.id"), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_pen_assignments_animal_id", "pen_assignments", ["animal_id"])
    op.create_index("ix_pen_assignments_pen_id", "pen_assignments", ["pen_id"])


def downgrade() -> None:
    op.drop_index("ix_pen_assignments_pen_id", table_name="pen_assignments")
    op.drop_index("ix_pen_assignments_animal_id", table_name="pen_assignments")
    op.drop_table("pen_assignments")
    op.drop_table("pens")

    for table_name in reversed(LOOKUP_TABLES):
        op.drop_table(table_name)
