"""Maliyet alanlari ekle: animals.purchase_cost, feed_distributions.total_cost, health_events.cost

Besi/damizlik isletmesinin maliyet-verimlilik-karlilik analizleri icin
gereken 3 temel fact alani. Hepsi nullable (backfill gerekmez, geriye
donuk uyumlu) ve TL tutar - tarihsel maliyet olarak hic degistirilmez;
USD karsiligi rapor katmaninda islem tarihi + TCMB kuruyla turetilir
(bkz. app/modules/fx).

Revision ID: 0014
Revises: 0013
Create Date: 2026-07-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("animals", sa.Column("purchase_cost", sa.Numeric(10, 2), nullable=True))
    op.add_column("feed_distributions", sa.Column("total_cost", sa.Numeric(10, 2), nullable=True))
    op.add_column("health_events", sa.Column("cost", sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("health_events", "cost")
    op.drop_column("feed_distributions", "total_cost")
    op.drop_column("animals", "purchase_cost")
