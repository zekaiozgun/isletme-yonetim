"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.feed.seed
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.lookup_helpers import seed_lookup_rows
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
    seed_lookup_rows(db, SEED_DATA)


def main() -> None:
    db = SessionLocal()
    try:
        run(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
