"""Death servis katmani.

create_death, Death kaydini olusturduktan sonra Animal.status_id/
status_date/death_reason_id alanlarini 'Oldu' olarak senkronize eder
(Anayasa m.8). Gercek kaynak (source of truth) deaths tablosudur.
update_death degisiklikleri yeniden senkronize eder; delete_death,
Animal.status'u 'Aktif'e dondurur.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError, NotFoundError
from app.core.lookup_helpers import get_lookup_by_code
from app.core.validators import require_date_order
from app.modules.animal.lookups import AnimalStatus
from app.modules.animal.models import Animal
from app.modules.animal.service import ACTIVE_STATUS_CODE
from app.modules.death.models import Death
from app.modules.death.schemas import DeathCreate
from app.modules.fx import service as fx_service
from app.modules.sale.models import Sale

DEAD_STATUS_CODE = "OLDU"


def _validate_death(db: Session, death: Death, animal: Animal | None) -> None:
    if animal is not None:
        require_date_order(animal.birth_date, "Doğum tarihi", death.death_date, "Ölüm tarihi")
        require_date_order(animal.entry_date, "Giriş tarihi", death.death_date, "Ölüm tarihi")
    already_sold = db.scalars(select(Sale.id).where(Sale.animal_id == death.animal_id)).first()
    if already_sold is not None:
        raise DomainError("Bu hayvan için zaten bir Satış kaydı var; aynı hayvan hem ölmüş hem satılmış olamaz.")


def create_death(db: Session, data: DeathCreate) -> Death:
    death = Death(**data.model_dump())
    animal = db.get(Animal, data.animal_id)
    _validate_death(db, death, animal)
    db.add(death)

    dead_status = get_lookup_by_code(db, AnimalStatus, DEAD_STATUS_CODE)
    if animal is not None:
        animal.status_id = dead_status.id
        animal.status_date = data.death_date
        animal.death_reason_id = data.death_reason_id

    db.commit()
    db.refresh(death)
    # Suru Kar/Zarar gibi raporlar bu tarihi CANLI cekmeye calismadan
    # dogrudan onbellekten bulsun diye (bkz. fx/service.py).
    fx_service.warm_rate_on_entry(db, death.death_date)
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

    animal = db.get(Animal, death.animal_id)
    _validate_death(db, death, animal)

    dead_status = get_lookup_by_code(db, AnimalStatus, DEAD_STATUS_CODE)
    if animal is not None:
        animal.status_id = dead_status.id
        animal.status_date = death.death_date
        animal.death_reason_id = death.death_reason_id

    db.commit()
    db.refresh(death)
    fx_service.warm_rate_on_entry(db, death.death_date)
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
