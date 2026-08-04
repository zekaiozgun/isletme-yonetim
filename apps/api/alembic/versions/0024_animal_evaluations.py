"""Evaluation module: evaluation_directions, evaluation_priorities, evaluation_reasons, animal_evaluations

Revision ID: 0024
Revises: 0023
Create Date: 2026-08-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0024"
down_revision: Union[str, None] = "0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evaluation_directions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code", name="uq_evaluation_directions_code"),
        sa.UniqueConstraint("name", name="uq_evaluation_directions_name"),
    )

    op.create_table(
        "evaluation_priorities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code", name="uq_evaluation_priorities_code"),
        sa.UniqueConstraint("name", name="uq_evaluation_priorities_name"),
    )

    op.create_table(
        "evaluation_reasons",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("direction_id", sa.Integer(), sa.ForeignKey("evaluation_directions.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code", name="uq_evaluation_reasons_code"),
        sa.UniqueConstraint("name", name="uq_evaluation_reasons_name"),
    )

    op.create_table(
        "animal_evaluations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("animal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("evaluation_date", sa.Date(), nullable=False),
        sa.Column("reason_id", sa.Integer(), sa.ForeignKey("evaluation_reasons.id"), nullable=False),
        sa.Column("priority_id", sa.Integer(), sa.ForeignKey("evaluation_priorities.id"), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_animal_evaluations_animal_id", "animal_evaluations", ["animal_id"])


def downgrade() -> None:
    op.drop_index("ix_animal_evaluations_animal_id", table_name="animal_evaluations")
    op.drop_table("animal_evaluations")
    op.drop_table("evaluation_reasons")
    op.drop_table("evaluation_priorities")
    op.drop_table("evaluation_directions")
