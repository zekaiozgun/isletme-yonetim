"""growth_valuation_checkpoints tablosu ekle (buyume degerleme cipalari)

Malzeme durumundaki (henuz Demirbasa gecmemis) hayvanlarin tahmini piyasa
degerini hesaplamak icin kullanicinin girdigi, cinsiyete ve yasa (3/6/9/12
ay) bagli gercek piyasa fiyatlari. 12 aylik cipa cinsiyete gore farkli bir
piyasa kategorisini temsil eder: Erkek icin "Besilik Erkek Dana", Disi
icin "Tohumlanmis/Gebe Duve" fiyati (bkz. app/modules/reports/service.py).

Revision ID: 0018
Revises: 0017
Create Date: 2026-07-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0018"
down_revision: Union[str, None] = "0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "growth_valuation_checkpoints",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("gender_id", sa.Integer(), sa.ForeignKey("genders.id"), nullable=False),
        sa.Column("age_months", sa.Integer(), nullable=False),
        sa.Column("value_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("age_months IN (3, 6, 9, 12)", name="ck_growth_checkpoint_age_months"),
        sa.UniqueConstraint("gender_id", "age_months", name="uq_growth_checkpoint_gender_age"),
    )


def downgrade() -> None:
    op.drop_table("growth_valuation_checkpoints")
