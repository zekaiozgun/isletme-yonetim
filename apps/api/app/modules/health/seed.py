"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.health.seed
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.lookup_helpers import seed_lookup_rows
from app.modules.health.lookups import Disease, DosageUnit, HealthEventType, MedicationType

SEED_DATA: dict[type, list[tuple[str, str]]] = {
    HealthEventType: [
        ("ASILAMA", "Asilama"),
        ("TEDAVI", "Tedavi"),
        ("MUAYENE", "Muayene"),
        ("HASTALIK_BILDIRIMI", "Hastalik Bildirimi"),
    ],
    MedicationType: [
        ("ASI", "Asi"),
        ("ANTIBIYOTIK", "Antibiyotik"),
        ("PARAZIT_ILACI", "Parazit Ilaci"),
        ("VITAMIN_MINERAL", "Vitamin / Mineral"),
        ("DIGER", "Diger"),
    ],
    DosageUnit: [
        ("ML", "ml"),
        ("MG", "mg"),
        ("CC", "cc"),
        ("DOZ", "doz"),
    ],
    # Disease listesi isletmeye/bolgeye gore degisir, kasitli olarak bos birakilir.
    Disease: [],
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
