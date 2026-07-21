"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.sale.seed
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.lookup_helpers import seed_lookup_rows
from app.modules.sale.lookups import SaleType

SEED_DATA: dict[type, list[tuple[str, str]]] = {
    SaleType: [
        ("CANLI", "Canli Satis"),
        ("KESIM", "Kesim Icin Satis"),
        ("DAMIZLIK", "Damizlik Satis"),
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
