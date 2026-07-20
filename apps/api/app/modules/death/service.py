"""Death servis katmani.

create_death, Death kaydini olusturduktan sonra Animal.status_id/
status_date/death_reason_id alanlarini 'Oldu' olarak senkronize eder
(Anayasa m.8). Gercek kaynak (source of truth) deaths tablosudur.
update_death degisiklikleri yeniden senkronize eder; delete_death,
Animal.status'u 'Aktif'e dondurur.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.lookup_helpers import get_lookup_by_code
from app.modules.animal.lookups import AnimalStatus
from app.modules.animal.models import Animal
from app.modules.animal.service import ACTIVE_STATUS_CODE
from app.modules.death.models import Death
from app.modules.death.schemas import DeathCreate

DEAD_STATUS_CODE = "OLDU"


def create_death(db: Session, data: DeathCreate) -> Death:
    death = Death(**data.model_dump())
    db.add(death)

    dead_status = get_lookup_by_code(db, AnimalStatus, DEAD_STATUS_CODE)
    animal = db.get(Animal, data.animal_id)
    if animal is not None:
        animal.status_id = dead_status.id
        animal.status_date = data.death_date
        animal.death_reason_id = data.death_reason_id

    db.commit()
    db.refresh(death)
    return death


def get_death(db: Session, death_id: int) -> Death:
    death = db.get(Death, death_id)
    if death is None:
        raise NotFoundError(f"Death bulunamadi: {death_id}")
    return death


def update_death(db: Session, death_id: int, data: DeathCreate) -> Death:
    death = get_death(db, death_id)
    for key, value in data.model_dump().items():
        setattr(death, key, value)

    dead_status = get_lookup_by_code(db, AnimalStatus, DEAD_STATUS_CODE)
    animal = db.get(Animal, death.animal_id)
    if animal is not None:
        animal.status_id = dead_status.id
        animal.status_date = death.death_date
        animal.death_reason_id = death.death_reason_id

    db.commit()
    db.refresh(death)
    return death


def delete_death(db: Session, death_id: int) -> None:
    death = get_death(db, death_id)
    animal = db.get(Animal, death.animal_id)
    db.delete(death)
    db.commit()

    if animal is not None:
        active_status = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE)
        animal.status_id = active_status.id
        animal.status_date = None
        animal.death_reason_id = None
        db.commit()


def list_deaths(db: Session) -> list[Death]:
    return list(db.scalars(select(Death).order_by(Death.death_date)).all())
