"""Breeding module: service_methods, pregnancy_check_methods, pregnancy_results,
breeding_events, pregnancy_checks

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LOOKUP_TABLES = ["service_methods", "pregnancy_check_methods", "pregnancy_results"]


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
        "breeding_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("dam_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("service_method_id", sa.Integer(), sa.ForeignKey("service_methods.id"), nullable=False),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column("sire_animal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=True),
        sa.Column("semen_batch_id", sa.Integer(), sa.ForeignKey("semen_batches.id"), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "(sire_animal_id IS NOT NULL) <> (semen_batch_id IS NOT NULL)",
            name="ck_breeding_events_sire_xor_semen",
        ),
    )
    op.create_index("ix_breeding_events_dam_id", "breeding_events", ["dam_id"])

    op.create_table(
        "pregnancy_checks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("breeding_event_id", sa.Integer(), sa.ForeignKey("breeding_events.id"), nullable=False),
        sa.Column("check_date", sa.Date(), nullable=False),
        sa.Column("method_id", sa.Integer(), sa.ForeignKey("pregnancy_check_methods.id"), nullable=False),
        sa.Column("result_id", sa.Integer(), sa.ForeignKey("pregnancy_results.id"), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_pregnancy_checks_breeding_event_id", "pregnancy_checks", ["breeding_event_id"])


def downgrade() -> None:
    op.drop_index("ix_pregnancy_checks_breeding_event_id", table_name="pregnancy_checks")
    op.drop_table("pregnancy_checks")
    op.drop_index("ix_breeding_events_dam_id", table_name="breeding_events")
    op.drop_table("breeding_events")

    for table_name in reversed(LOOKUP_TABLES):
        op.drop_table(table_name)
