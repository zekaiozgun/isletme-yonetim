"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.weight.seed
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.lookup_helpers import seed_lookup_rows
from app.modules.weight.lookups import WeighingMethod

SEED_DATA: dict[type, list[tuple[str, str]]] = {
    WeighingMethod: [
        ("DIJITAL", "Dijital Kantar"),
        ("ELLE", "Elle Tarti"),
        ("BANT", "Bant Olcumu (Tahmini)"),
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
