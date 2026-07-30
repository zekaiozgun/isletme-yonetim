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
        ("SAROLE", "Şarole (Charolais)"),
        ("LIMUZIN", "Limuzin (Limousin)"),
        ("ANGUS", "Angus"),
        ("HEREFORD", "Hereford"),
        ("MONTOFON", "Montofon"),
        ("HOLSTEIN", "Holstein"),
        ("YERLI", "Yerli Sığır"),
        ("DIGER", "Diğer"),
    ],
    Gender: [
        ("ERKEK", "Erkek"),
        ("DISI", "Dişi"),
    ],
    BirthType: [
        ("NORMAL", "Normal Doğum"),
        ("GUC", "Güç Doğum (Distoni)"),
        ("SEZARYEN", "Sezaryen"),
        ("OLU", "Ölü Doğum"),
    ],
    LitterType: [
        ("TEKIZ", "Tekiz"),
        ("IKIZ", "İkiz"),
        ("UCUZ", "Üçüz"),
    ],
    HornStatus: [
        ("BOYNUZLU", "Boynuzlu"),
        ("BOYNUZSUZ", "Boynuzsuz (Polled)"),
        ("ALINMIS", "Boynuzu Alınmış (Dehorned)"),
    ],
    EntrySource: [
        ("DOGUM", "Doğum"),
        ("SATIN_ALMA", "Satın Alma"),
        ("DEVIR", "Devir / Nakil"),
        ("KIRALAMA", "Kiralama"),
        ("DIGER", "Diğer"),
    ],
    AnimalStatus: [
        ("AKTIF", "Aktif"),
        ("SATILDI", "Satıldı"),
        ("OLDU", "Öldü"),
        ("KESILDI", "Kesildi"),
        ("HATALI_GIRIS", "Hatalı Giriş İptali"),
    ],
    DeathReason: [
        ("HASTALIK", "Hastalık"),
        ("KAZA", "Kaza"),
        ("DOGUM_KOMPLIKASYONU", "Doğum Komplikasyonu"),
        ("YASLILIK", "Yaşlılık"),
        ("PREDASYON", "Predasyon (Yırtıcı Saldırısı)"),
        ("BILINMEYEN", "Bilinmeyen"),
        ("DIGER", "Diğer"),
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
