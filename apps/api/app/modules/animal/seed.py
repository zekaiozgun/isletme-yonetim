"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.animal.seed
Idempotenttir: mevcut kodlar tekrar eklenmez (code alanina gore upsert-benzeri kontrol).
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.lookup_helpers import seed_lookup_rows
from app.modules.animal.lookups import (
    AnimalStatus,
    BirthType,
    Breed,
    DeathReason,
    EntrySource,
    Gender,
    HornStatus,
    LitterType,
    SourceFarm,
)

SEED_DATA: dict[type, list[tuple[str, str]]] = {
    Breed: [
        ("SIMENTAL", "Simental"),
        ("SAROLE", "Sarole (Charolais)"),
        ("LIMUZIN", "Limuzin (Limousin)"),
        ("ANGUS", "Angus"),
        ("HEREFORD", "Hereford"),
        ("MONTOFON", "Montofon"),
        ("HOLSTEIN", "Holstein"),
        ("YERLI", "Yerli Sigir"),
        ("DIGER", "Diger"),
    ],
    Gender: [
        ("ERKEK", "Erkek"),
        ("DISI", "Disi"),
    ],
    BirthType: [
        ("NORMAL", "Normal Dogum"),
        ("GUC", "Guc Dogum (Distoni)"),
        ("SEZARYEN", "Sezaryen"),
        ("OLU", "Olu Dogum"),
    ],
    LitterType: [
        ("TEKIZ", "Tekiz"),
        ("IKIZ", "Ikiz"),
        ("UCUZ", "Ucuz"),
    ],
    HornStatus: [
        ("BOYNUZLU", "Boynuzlu"),
        ("BOYNUZSUZ", "Boynuzsuz (Polled)"),
        ("ALINMIS", "Boynuzu Alinmis (Dehorned)"),
    ],
    EntrySource: [
        ("DOGUM", "Doğum"),
        ("SATIN_ALMA", "Satin Alma"),
        ("DEVIR", "Devir / Nakil"),
        ("KIRALAMA", "Kiralama"),
        ("DIGER", "Diger"),
    ],
    AnimalStatus: [
        ("AKTIF", "Aktif"),
        ("SATILDI", "Satildi"),
        ("OLDU", "Oldu"),
        ("KESILDI", "Kesildi"),
    ],
    DeathReason: [
        ("HASTALIK", "Hastalik"),
        ("KAZA", "Kaza"),
        ("DOGUM_KOMPLIKASYONU", "Dogum Komplikasyonu"),
        ("YASLILIK", "Yaslilik"),
        ("PREDASYON", "Predasyon (Yirtici Saldirisi)"),
        ("BILINMEYEN", "Bilinmeyen"),
        ("DIGER", "Diger"),
    ],
    # SourceFarm kasitli olarak bos birakilir: gercek kaynak isletmeler
    # operasyonel veri olarak ihtiyac duyuldukca eklenir.
    SourceFarm: [],
}


def run(db: Session) -> None:
    seed_lookup_rows(db, SEED_DATA)


def main() -> None:
    db = SessionLocal()
    try:
        run(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
