"""sales.carcass_weight_kg ekle (kesim satislarinda karkas agirligi)

sale_weight_kg her zaman canli agirlik anlamina geliyordu ama bu hicbir
yerde acikca belirtilmiyordu - "Kesim Icin Satis" (sale_type_id=KESIM)
secildiginde, ayrica karkas agirligi da kaydedilebilsin diye eklendi.
Her iki alan da opsiyonel (canli agirlik girilmeyen kesim satislari da
olabilir), tum satis tiplerinde gosterilir - "Kesim" disinda anlamsizsa
kullanici bos birakir.

Revision ID: 0023
Revises: 0022
Create Date: 2026-08-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0023"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sales", sa.Column("carcass_weight_kg", sa.Numeric(6, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("sales", "carcass_weight_kg")
