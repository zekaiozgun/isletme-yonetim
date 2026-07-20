"""Animal master entity + master data (lookup) tables

Revision ID: 0001
Revises:
Create Date: 2026-07-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LOOKUP_TABLES = [
    "breeds",
    "genders",
    "birth_types",
    "litter_types",
    "horn_statuses",
    "source_farms",
    "entry_sources",
    "animal_statuses",
    "death_reasons",
]


def _create_lookup_table(name: str) -> None:
    op.create_table(
        name,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("code", name=f"uq_{name}_code"),
        sa.UniqueConstraint("name", name=f"uq_{name}_name"),
    )


def upgrade() -> None:
    for table_name in LOOKUP_TABLES:
        _create_lookup_table(table_name)

    op.create_table(
        "animals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # Kimlik
        sa.Column("tag_number", sa.String(length=32), nullable=False),
        sa.Column("rfid", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=True),
        # Dogum
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("birth_type_id", sa.Integer(), sa.ForeignKey("birth_types.id"), nullable=True),
        sa.Column("birth_weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("litter_type_id", sa.Integer(), sa.ForeignKey("litter_types.id"), nullable=True),
        # Soy
        sa.Column("mother_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=True),
        sa.Column("father_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=True),
        sa.Column("breed_id", sa.Integer(), sa.ForeignKey("breeds.id"), nullable=True),
        sa.Column("crossbreed_ratio", sa.Numeric(5, 2), nullable=True),
        # Fiziksel
        sa.Column("gender_id", sa.Integer(), sa.ForeignKey("genders.id"), nullable=False),
        sa.Column("horn_status_id", sa.Integer(), sa.ForeignKey("horn_statuses.id"), nullable=True),
        # Mensei
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("source_farm_id", sa.Integer(), sa.ForeignKey("source_farms.id"), nullable=True),
        sa.Column("entry_source_id", sa.Integer(), sa.ForeignKey("entry_sources.id"), nullable=False),
        # Statu
        sa.Column("status_id", sa.Integer(), sa.ForeignKey("animal_statuses.id"), nullable=False),
        sa.Column("status_date", sa.Date(), nullable=True),
        sa.Column("death_reason_id", sa.Integer(), sa.ForeignKey("death_reasons.id"), nullable=True),
        # Not
        sa.Column("note", sa.String(length=500), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("tag_number", name="uq_animals_tag_number"),
        sa.UniqueConstraint("rfid", name="uq_animals_rfid"),
    )

    op.create_index("ix_animals_breed_id", "animals", ["breed_id"])
    op.create_index("ix_animals_status_id", "animals", ["status_id"])
    op.create_index("ix_animals_mother_id", "animals", ["mother_id"])
    op.create_index("ix_animals_father_id", "animals", ["father_id"])


def downgrade() -> None:
    op.drop_index("ix_animals_father_id", table_name="animals")
    op.drop_index("ix_animals_mother_id", table_name="animals")
    op.drop_index("ix_animals_status_id", table_name="animals")
    op.drop_index("ix_animals_breed_id", table_name="animals")
    op.drop_table("animals")

    for table_name in reversed(LOOKUP_TABLES):
        op.drop_table(table_name)
