"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.pen.seed
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.lookup_helpers import seed_lookup_rows
from app.modules.pen.lookups import PenAssignmentReason, PenType

SEED_DATA: dict[type, list[tuple[str, str]]] = {
    PenType: [
        ("DOGUM", "Dogum Padoku"),
        ("BESI", "Besi Padoku"),
        ("KARANTINA", "Karantina"),
        ("HASTANE", "Hastane Padogu"),
        ("BEKLEME", "Bekleme Padoku"),
    ],
    PenAssignmentReason: [
        ("BUYUME", "Buyume"),
        ("SAGLIK", "Saglik"),
        ("CINSIYET_AYRIMI", "Cinsiyet Ayrimi"),
        ("DOGUM", "Dogum"),
        ("DIGER", "Diger"),
    ],
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
