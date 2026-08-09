"""Rasyon unsuruna uygulanacak yas grubu (Tum Hayvanlar/Buzagi/Yetiskin)

Anne-yavru padoklarinda buzagilar, ayni padoktaki yetiskinlerle HOMOJEN
sayilip tam porsiyon yiyormus gibi hesaplaniyordu. Yeni ration_item_scopes
lookup'i + ration_items.scope_id ile bir rasyon kalemi artik sadece
buzagilara, sadece yetiskinlere veya (varsayilan, mevcut davranis) tum
padoga uygulanabilir.

Revision ID: 0025
Revises: 0024
Create Date: 2026-08-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0025"
down_revision: Union[str, None] = "0024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_SCOPE_CODE = "TUMU"


def upgrade() -> None:
    op.create_table(
        "ration_item_scopes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO ration_item_scopes (code, name, is_active) VALUES
            ('TUMU', 'Tüm Hayvanlar', true),
            ('BUZAGI', 'Sadece Buzağı (0-7 Ay)', true),
            ('YETISKIN', 'Sadece Yetişkin (7+ Ay)', true)
            """
        )
    )

    op.add_column("ration_items", sa.Column("scope_id", sa.Integer(), sa.ForeignKey("ration_item_scopes.id"), nullable=True))
    connection.execute(
        sa.text(
            f"""
            UPDATE ration_items
            SET scope_id = (SELECT id FROM ration_item_scopes WHERE code = '{DEFAULT_SCOPE_CODE}')
            WHERE scope_id IS NULL
            """
        )
    )
    op.alter_column("ration_items", "scope_id", nullable=False)


def downgrade() -> None:
    op.drop_column("ration_items", "scope_id")
    op.drop_table("ration_item_scopes")
