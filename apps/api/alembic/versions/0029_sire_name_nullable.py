"""sires.name'i nullable yap

Suruye ait bir boganin (animal_id dolu) kimligi artik Animal kaydindan
turetiliyor (bkz. genetic_resource/models.py Sire.display_name) - kendi
name alani sadece dis kaynakli (animal_id=None) bogalarda zorunlu
(schemas.SireCreate validasyonunda uygulanir). Mevcut herd-linked
kayitlarin name'i bilerek DEGISTIRILMEZ/temizlenmez - eski deger orada
durur ama artik hicbir yerde okunmaz (display_name Animal'a dusuyor),
kullanici isterse Boğalar formundan elle bosaltabilir.

Revision ID: 0029
Revises: 0028
Create Date: 2026-09-12

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0029"
down_revision: Union[str, None] = "0028"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("sires", "name", existing_type=sa.String(length=120), nullable=True)


def downgrade() -> None:
    op.alter_column("sires", "name", existing_type=sa.String(length=120), nullable=False)
