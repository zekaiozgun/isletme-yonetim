"""growth_valuation_checkpoints: age_months -> category_code, value_usd -> value_try

Kullanici geri bildirimi: cipa degerleri USD degil TL olarak girilmeli
(diger tum maliyet fact'leri gibi - USD karsiligi rapor uretilirken TCMB
kuruyla turetilir, Anayasa m.4/m.5). Ayrica sadece genc hayvan buyume
egrisi (3/6/9/12 ay) degil, olgun (Demirbasa gecmis) bir disinin GUNCEL
ureme durumuna (Gebe/Bos) gore piyasa degeri de gerekiyor - bu yuzden
sabit age_months yerine 6 sabit kategoriden birini tutan category_code
kullanilir: AGE_3, AGE_6, AGE_9, AGE_12, GEBE, BOS.

Revision ID: 0019
Revises: 0018
Create Date: 2026-07-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0019"
down_revision: Union[str, None] = "0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_growth_checkpoint_age_months", "growth_valuation_checkpoints", type_="check")
    op.drop_constraint("uq_growth_checkpoint_gender_age", "growth_valuation_checkpoints", type_="unique")

    op.add_column("growth_valuation_checkpoints", sa.Column("category_code", sa.String(length=16), nullable=True))
    op.execute("UPDATE growth_valuation_checkpoints SET category_code = 'AGE_' || age_months::text")
    op.alter_column("growth_valuation_checkpoints", "category_code", nullable=False)
    op.drop_column("growth_valuation_checkpoints", "age_months")

    op.alter_column("growth_valuation_checkpoints", "value_usd", new_column_name="value_try")

    op.create_check_constraint(
        "ck_growth_checkpoint_category",
        "growth_valuation_checkpoints",
        "category_code IN ('AGE_3','AGE_6','AGE_9','AGE_12','GEBE','BOS')",
    )
    op.create_unique_constraint(
        "uq_growth_checkpoint_gender_category", "growth_valuation_checkpoints", ["gender_id", "category_code"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_growth_checkpoint_gender_category", "growth_valuation_checkpoints", type_="unique")
    op.drop_constraint("ck_growth_checkpoint_category", "growth_valuation_checkpoints", type_="check")

    op.alter_column("growth_valuation_checkpoints", "value_try", new_column_name="value_usd")

    op.add_column("growth_valuation_checkpoints", sa.Column("age_months", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE growth_valuation_checkpoints SET age_months = CAST(substring(category_code from 5) AS integer) "
        "WHERE category_code LIKE 'AGE_%'"
    )
    op.execute("DELETE FROM growth_valuation_checkpoints WHERE category_code IN ('GEBE', 'BOS')")
    op.alter_column("growth_valuation_checkpoints", "age_months", nullable=False)
    op.drop_column("growth_valuation_checkpoints", "category_code")

    op.create_check_constraint(
        "ck_growth_checkpoint_age_months", "growth_valuation_checkpoints", "age_months IN (3, 6, 9, 12)"
    )
    op.create_unique_constraint(
        "uq_growth_checkpoint_gender_age", "growth_valuation_checkpoints", ["gender_id", "age_months"]
    )
