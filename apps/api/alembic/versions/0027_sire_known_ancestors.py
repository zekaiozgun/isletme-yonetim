"""Dış kaynaklı boğada bilinen ebeveyn kimlikleri (soy ağacı Faz 2)

Dış kaynaklı (suni tohumlama) bir boğanın kendi ebeveyni sürüye ait
değildir, tam bir Animal kaydı açılmaz - ama katalogda çoğunlukla
bilinir (kimlik no + ad). Girilirse soy ağacı bu boğa düğümünde
sonlanmak yerine bir nesil daha derine iner.

Revision ID: 0027
Revises: 0026
Create Date: 2026-08-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0027"
down_revision: Union[str, None] = "0026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sires", sa.Column("known_sire_registry_no", sa.String(length=64), nullable=True))
    op.add_column("sires", sa.Column("known_sire_name", sa.String(length=120), nullable=True))
    op.add_column("sires", sa.Column("known_dam_registry_no", sa.String(length=64), nullable=True))
    op.add_column("sires", sa.Column("known_dam_name", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("sires", "known_dam_name")
    op.drop_column("sires", "known_dam_registry_no")
    op.drop_column("sires", "known_sire_name")
    op.drop_column("sires", "known_sire_registry_no")
