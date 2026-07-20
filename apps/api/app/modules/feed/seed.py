"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.feed.seed
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.feed.lookups import FeedType, FeedUnit

SEED_DATA: dict[type, list[tuple[str, str]]] = {
    FeedType: [
        ("KABA_YEM", "Kaba Yem"),
        ("KESIF_YEM", "Kesif Yem"),
        ("SILAJ", "Silaj"),
        ("MINERAL_VITAMIN", "Mineral / Vitamin"),
    ],
    FeedUnit: [
        ("KG", "kg"),
        ("TON", "ton"),
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
