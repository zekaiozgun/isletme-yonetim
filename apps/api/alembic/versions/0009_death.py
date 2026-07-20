"""Death module: disposal_methods, deaths

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "disposal_methods",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code", name="uq_disposal_methods_code"),
        sa.UniqueConstraint("name", name="uq_disposal_methods_name"),
    )

    op.create_table(
        "deaths",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("animal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("death_date", sa.Date(), nullable=False),
        sa.Column("death_reason_id", sa.Integer(), sa.ForeignKey("death_reasons.id"), nullable=False),
        sa.Column("disposal_method_id", sa.Integer(), sa.ForeignKey("disposal_methods.id"), nullable=False),
        sa.Column("necropsy_performed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("animal_id", name="uq_deaths_animal_id"),
    )


def downgrade() -> None:
    op.drop_table("deaths")
    op.drop_table("disposal_methods")
