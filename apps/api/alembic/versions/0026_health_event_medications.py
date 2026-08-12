"""Sağlık olayı başına birden fazla ilaç girilebilsin

Bir muayene/tedavide genelde birden fazla ilaç birlikte kullanılır, ama
health_events tek bir medication_id/dosage_amount/dosage_unit_id
tutuyordu (kullanıcı geri bildirimi). Yeni health_event_medications alt
tablosu ile bir sağlık olayına istenildiği kadar ilaç satırı eklenebilir.
Mevcut tekli ilaç kayıtları alt tabloya taşınır, veri kaybı olmaz.

Revision ID: 0026
Revises: 0025
Create Date: 2026-08-12

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0026"
down_revision: Union[str, None] = "0025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "health_event_medications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "health_event_id", sa.Integer(), sa.ForeignKey("health_events.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("medication_id", sa.Integer(), sa.ForeignKey("medications.id"), nullable=False),
        sa.Column("dosage_amount", sa.Numeric(8, 2), nullable=True),
        sa.Column("dosage_unit_id", sa.Integer(), sa.ForeignKey("dosage_units.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        "ix_health_event_medications_health_event_id", "health_event_medications", ["health_event_id"]
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO health_event_medications
                (health_event_id, medication_id, dosage_amount, dosage_unit_id, created_at, updated_at)
            SELECT id, medication_id, dosage_amount, dosage_unit_id, now(), now()
            FROM health_events
            WHERE medication_id IS NOT NULL
            """
        )
    )

    op.drop_column("health_events", "medication_id")
    op.drop_column("health_events", "dosage_amount")
    op.drop_column("health_events", "dosage_unit_id")


def downgrade() -> None:
    op.add_column("health_events", sa.Column("medication_id", sa.Integer(), sa.ForeignKey("medications.id"), nullable=True))
    op.add_column("health_events", sa.Column("dosage_amount", sa.Numeric(8, 2), nullable=True))
    op.add_column(
        "health_events", sa.Column("dosage_unit_id", sa.Integer(), sa.ForeignKey("dosage_units.id"), nullable=True)
    )

    connection = op.get_bind()
    # Kayipli: bir olayin birden fazla ilaci varsa sadece EN ESKI (ilk) satir geri yazilir.
    connection.execute(
        sa.text(
            """
            UPDATE health_events he
            SET medication_id = hem.medication_id,
                dosage_amount = hem.dosage_amount,
                dosage_unit_id = hem.dosage_unit_id
            FROM (
                SELECT DISTINCT ON (health_event_id) health_event_id, medication_id, dosage_amount, dosage_unit_id
                FROM health_event_medications
                ORDER BY health_event_id, id
            ) hem
            WHERE he.id = hem.health_event_id
            """
        )
    )
    op.drop_table("health_event_medications")
