"""Genetic Resource module: sires, semen_batches

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sires",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("registry_no", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("breed_id", sa.Integer(), sa.ForeignKey("breeds.id"), nullable=False),
        sa.Column("animal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=True),
        sa.Column("is_external", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("registry_no", name="uq_sires_registry_no"),
        sa.UniqueConstraint("animal_id", name="uq_sires_animal_id"),
    )

    op.create_table(
        "semen_batches",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sire_id", sa.Integer(), sa.ForeignKey("sires.id"), nullable=False),
        sa.Column("batch_no", sa.String(length=64), nullable=False),
        sa.Column("supplier_farm_id", sa.Integer(), sa.ForeignKey("source_farms.id"), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("straw_count", sa.Integer(), nullable=False),
        sa.Column("storage_location", sa.String(length=120), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("sire_id", "batch_no", name="uq_semen_batches_sire_batch_no"),
    )
    op.create_index("ix_semen_batches_sire_id", "semen_batches", ["sire_id"])


def downgrade() -> None:
    op.drop_index("ix_semen_batches_sire_id", table_name="semen_batches")
    op.drop_table("semen_batches")
    op.drop_table("sires")
