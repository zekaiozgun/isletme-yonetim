"""exchange_rates tablosu ekle (TCMB USD/TRY kur onbellegi)

Rapor katmaninin, maliyet fact'lerini (TL) islem tarihindeki TCMB USD
satis kuruyla USD karsiligina cevirebilmesi icin kullanilan onbellek
tablosu (bkz. app/modules/fx). Hicbir maliyet tablosuna kur alani
eklenmez - tarihsel TL maliyet hic degismez, USD karsiligi rapor
uretilirken bu tablo + islem tarihi kullanilarak turetilir.

Revision ID: 0015
Revises: 0014
Create Date: 2026-07-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015"
down_revision: Union[str, None] = "0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exchange_rates",
        sa.Column("rate_date", sa.Date(), primary_key=True),
        sa.Column("usd_try_selling", sa.Numeric(10, 4), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("exchange_rates")
