"""sires.is_placeholder - menşei bilinmeyen hayvanların yer tutucu babası

U.HEREFORD/U.ANGUS gibi kayıtlar gerçek bir boğa değil, "babası bilinmeyen
(satın alınan) hayvan" için konmuş yer tutucu - akrabalık kontrolünde
ortak ata sayılmamalı. Bayrak kullanıcı tarafından Boğalar formundan
işaretlenir; sadece kullanıcının açıkça yer tutucu olarak onayladığı iki
mevcut kayıt (U.ANGUS, U.HEREFORD) burada işaretlenir.

Revision ID: 0031
Revises: 0030
Create Date: 2026-10-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0031"
down_revision: Union[str, None] = "0030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sires", sa.Column("is_placeholder", sa.Boolean(), nullable=False, server_default="false"))
    op.get_bind().execute(
        sa.text(
            "UPDATE sires SET is_placeholder = true "
            "WHERE animal_id IS NULL AND name IN ('U.ANGUS', 'U.HEREFORD')"
        )
    )


def downgrade() -> None:
    op.drop_column("sires", "is_placeholder")
