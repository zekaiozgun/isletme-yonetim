"""animals.is_locked ekle (Calisan cift-onay kilidi)

Calisan rolundeki bir kullanici cift onayla bir hayvan kaydi
olusturdugunda is_locked=true olur; bu kayit Calisan tarafindan bir daha
duzenlenemez/silinemez (YONETICI icin kisitlama yoktur). Duzeltme yolu
"Hatali Giris Iptali" statusune gecis (cancel-entry endpoint'i).

Revision ID: 0013
Revises: 0012
Create Date: 2026-07-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "animals",
        sa.Column("is_locked", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("animals", "is_locked")
