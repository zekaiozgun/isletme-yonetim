"""Health module: health_event_types, diseases, medication_types, dosage_units,
medications, health_events

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LOOKUP_TABLES = ["health_event_types", "diseases", "medication_types", "dosage_units"]


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
        "medications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("active_ingredient", sa.String(length=120), nullable=True),
        sa.Column("medication_type_id", sa.Integer(), sa.ForeignKey("medication_types.id"), nullable=False),
        sa.Column("withdrawal_period_days", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_medications_name"),
    )

    op.create_table(
        "health_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("animal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("event_type_id", sa.Integer(), sa.ForeignKey("health_event_types.id"), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("disease_id", sa.Integer(), sa.ForeignKey("diseases.id"), nullable=True),
        sa.Column("medication_id", sa.Integer(), sa.ForeignKey("medications.id"), nullable=True),
        sa.Column("dosage_amount", sa.Numeric(8, 2), nullable=True),
        sa.Column("dosage_unit_id", sa.Integer(), sa.ForeignKey("dosage_units.id"), nullable=True),
        sa.Column("veterinarian_note", sa.String(length=500), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_health_events_animal_id", "health_events", ["animal_id"])


def downgrade() -> None:
    op.drop_index("ix_health_events_animal_id", table_name="health_events")
    op.drop_table("health_events")
    op.drop_table("medications")

    for table_name in reversed(LOOKUP_TABLES):
        op.drop_table(table_name)
