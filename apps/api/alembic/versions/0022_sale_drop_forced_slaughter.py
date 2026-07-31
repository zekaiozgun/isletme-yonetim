"""sales.is_forced_slaughter kaldir (ZORUNLU satis tipiyle cakisiyordu)

0021'de eklenen bu bayrak, sale_types tablosunda zaten var olan "ZORUNLU"
(Zorunlu Kesim) lookup degeriyle ayni anlami tasidigi anlasildiktan sonra
kaldirildi - iki farkli yoldan ayni facti isaretlemek yerine mevcut
sale_type_id = ZORUNLU kullanimina devam edilecek.

Revision ID: 0022
Revises: 0021
Create Date: 2026-07-31

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0022"
down_revision: Union[str, None] = "0021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("sales", "is_forced_slaughter")


def downgrade() -> None:
    op.add_column(
        "sales",
        sa.Column("is_forced_slaughter", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
