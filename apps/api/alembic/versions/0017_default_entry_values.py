"""Varsayilan giris degerleri (bir kerelik veri doldurma) + entry_sources sadelestirme

Kullanicinin belirttigi standart giris degerleri, entry_value BOS OLAN
(daha once elle girilmis gercek bir tutari EZMEZ) tum hayvanlara -
statu farketmeksizin (Aktif/Satildi/Oldu/Hatali Giris dahil, gecmis
Kârlilik Raporu hesaplarinin da dogru olmasi icin):

  - Satin Alma + Disi (inek)  -> 145.000 TL
  - Satin Alma + Erkek (boga) -> 160.000 TL
  - Dogum (her cinsiyet, buzagi) -> 70.000 TL (biyolojik varlik
    muhasebesi: dogan bir buzagi da bir degerle isletmeye giren bir
    "urun"dur)

Ayrica isletmede fiilen kullanilmayan 3 giris kaynagi (Devir/Nakil,
Kiralama, Diger) is_active=false yapilarak secim listelerinden
gizlenir (silinmez - varsa gecmis kayitlarla referans butunlugu
bozulmaz, kullanici isterse Master Data ekranindan tekrar aktif eder).

Revision ID: 0017
Revises: 0016
Create Date: 2026-07-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            UPDATE animals
            SET entry_value = 145000
            WHERE entry_value IS NULL
              AND gender_id = (SELECT id FROM genders WHERE code = 'DISI')
              AND entry_source_id = (SELECT id FROM entry_sources WHERE code = 'SATIN_ALMA')
            """
        )
    )
    connection.execute(
        sa.text(
            """
            UPDATE animals
            SET entry_value = 160000
            WHERE entry_value IS NULL
              AND gender_id = (SELECT id FROM genders WHERE code = 'ERKEK')
              AND entry_source_id = (SELECT id FROM entry_sources WHERE code = 'SATIN_ALMA')
            """
        )
    )
    connection.execute(
        sa.text(
            """
            UPDATE animals
            SET entry_value = 70000
            WHERE entry_value IS NULL
              AND entry_source_id = (SELECT id FROM entry_sources WHERE code = 'DOGUM')
            """
        )
    )
    connection.execute(
        sa.text("UPDATE entry_sources SET is_active = false WHERE code IN ('DEVIR', 'KIRALAMA', 'DIGER')")
    )


def downgrade() -> None:
    # entry_value doldurma islemi geri alinamaz (hangi satirlarin bu
    # migration tarafindan doldurulup hangisinin daha sonra elle
    # degistirildigini ayirt etmenin guvenilir bir yolu yok) - sadece
    # entry_sources'in aktiflik durumu geri alinir.
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE entry_sources SET is_active = true WHERE code IN ('DEVIR', 'KIRALAMA', 'DIGER')")
    )
