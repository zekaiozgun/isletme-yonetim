"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.pen.seed
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
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
    for model, rows in SEED_DATA.items():
        existing_codes = {code for (code,) in db.query(model.code).all()}
        for code, name in rows:
            if code in existing_codes:
                continue
            db.add(model(code=code, name=name))
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        run(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
