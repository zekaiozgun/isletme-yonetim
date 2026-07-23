"""animals.purchase_cost -> animals.entry_value olarak yeniden adlandir

purchase_cost yalnizca satin alinan hayvanlar icin anlamli bir isimdi.
Isletmede DOGAN hayvanlar da (biyolojik varlik muhasebesi geregi) dogum
aninda bir degerle isletmeye girer - olurse bu deger dogrudan zarar
yazilir (depoda curuyen stok gibi). Alan, kaynaktan bagimsiz tek bir
"giris degeri" kavramini yansitacak sekilde yeniden adlandirildi; mevcut
veri (varsa) RENAME COLUMN ile korunur, kayip olmaz.

Revision ID: 0016
Revises: 0015
Create Date: 2026-07-24

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("animals", "purchase_cost", new_column_name="entry_value")


def downgrade() -> None:
    op.alter_column("animals", "entry_value", new_column_name="purchase_cost")
