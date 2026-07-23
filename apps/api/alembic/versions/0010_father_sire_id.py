"""Animal.father_id -> father_sire_id (Sires tablosuna referans)

Baba, artik dogrudan bir Animal kaydina degil, Genetic Resource
modulundeki Sire (Boga) katalogruna referans verir - hem suruye ait
fiziki bogalar hem de yalnizca suni tohumlama icin kayitli dis kaynakli
bogalar bu tabloda zaten birlikte tutuluyor. Bu sayede bir bogayi Baba
olarak secebilmek icin ayrica tam bir Animal kaydi acmaya gerek kalmaz.

father_id, deploy oncesi hicbir ortamda (yerel/production) dolu
degildi - veri kaybi riski yok.

Revision ID: 0010
Revises: 0009
Create Date: 2026-07-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_animals_father_id", table_name="animals")
    op.drop_column("animals", "father_id")
    op.add_column("animals", sa.Column("father_sire_id", sa.Integer(), sa.ForeignKey("sires.id"), nullable=True))
    op.create_index("ix_animals_father_sire_id", "animals", ["father_sire_id"])


def downgrade() -> None:
    op.drop_index("ix_animals_father_sire_id", table_name="animals")
    op.drop_column("animals", "father_sire_id")
    op.add_column(
        "animals", sa.Column("father_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=True)
    )
    op.create_index("ix_animals_father_id", "animals", ["father_id"])
