"""sales.is_forced_slaughter ekle (zorunlu kesim isareti)

Hayvan yaralanma/hastalik gibi bir zorunluluktan dolayi (planlanan
zamanindan once, tipik olarak dusuk fiyata) kesime satildiysa
isaretlenebilir - boylece Hayvan Karlilik Raporu'nda zarar olarak
gorunen bu satislar ayrica filtrelenip/raporlanabilir. Nedeni tekrar
tutulmaz, zaten Saglik Olaylari'nda kayitlidir.

Revision ID: 0021
Revises: 0020
Create Date: 2026-07-31

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0021"
down_revision: Union[str, None] = "0020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sales",
        sa.Column("is_forced_slaughter", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("sales", "is_forced_slaughter")
