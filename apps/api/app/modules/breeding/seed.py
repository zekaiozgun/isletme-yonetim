"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.breeding.seed
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.lookup_helpers import seed_lookup_rows
from app.modules.breeding.lookups import PregnancyCheckMethod, PregnancyResult, ServiceMethod

SEED_DATA: dict[type, list[tuple[str, str]]] = {
    ServiceMethod: [
        ("DOGAL", "Dogal Asim"),
        ("SUNI_TOHUMLAMA", "Suni Tohumlama"),
        ("EMBRIYO_TRANSFERI", "Embriyo Transferi"),
    ],
    PregnancyCheckMethod: [
        ("REKTAL", "Rektal Muayene"),
        ("ULTRASON", "Ultrason"),
        ("KAN_TESTI", "Kan Testi"),
    ],
    PregnancyResult: [
        ("GEBE", "Gebe"),
        ("BOS", "Bos"),
        ("SUPHELI", "Supheli"),
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
