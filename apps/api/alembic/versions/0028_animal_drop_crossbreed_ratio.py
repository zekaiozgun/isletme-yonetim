"""animals.crossbreed_ratio sütununu kaldır (soy ağacı Faz 6)

crossbreed_ratio, elle girilen/onaylanan bir alandı - Anayasa m.4/m.5'e
aykırıydı (türetilebilen bir değer saklanıyordu). Yerine, mevcut soy
ağacı (mother_id/father_sire_id zinciri) üzerinden istek anında
hesaplanan bir "Genetik Karma" raporu geliyor (bkz. reports/service.py).
Hiçbir gerçek veri bu alana girilmediği için (kullanıcı onayı) veri
taşıma/yedekleme gerekmiyor.

Revision ID: 0028
Revises: 0027
Create Date: 2026-08-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0028"
down_revision: Union[str, None] = "0027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("animals", "crossbreed_ratio")


def downgrade() -> None:
    op.add_column("animals", sa.Column("crossbreed_ratio", sa.Numeric(5, 2), nullable=True))
