"""Tum modullerin lookup seed'lerini tek seferde calistirir.

Calistirma: python -m app.seed_all

Her modulun kendi seed.py'si idempotent (mevcut code'lari atlar), bu
yuzden bu script container her ayaga kalktiginda tekrar calistirilabilir.
"""

from app.core.database import SessionLocal
from app.modules.animal import seed as animal_seed
from app.modules.breeding import seed as breeding_seed
from app.modules.death import seed as death_seed
from app.modules.feed import seed as feed_seed
from app.modules.health import seed as health_seed
from app.modules.pen import seed as pen_seed
from app.modules.sale import seed as sale_seed
from app.modules.weight import seed as weight_seed

SEED_MODULES = [
    pen_seed,
    animal_seed,
    breeding_seed,
    death_seed,
    feed_seed,
    health_seed,
    sale_seed,
    weight_seed,
]


def main() -> None:
    db = SessionLocal()
    try:
        for module in SEED_MODULES:
            module.run(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
