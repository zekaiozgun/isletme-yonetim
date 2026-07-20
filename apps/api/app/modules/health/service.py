"""Health servis katmani.

withdrawal_end_date (ilac arinma bitis tarihi) DB'de saklanmaz;
event_date + medication.withdrawal_period_days ile burada hesaplanir
(Anayasa m.4/m.5). Ilac baglantisi olmayan olaylarda (orn. Muayene) None
doner.
"""

import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.health.models import HealthEvent, Medication
from app.modules.health.schemas import HealthEventCreate, MedicationCreate


def create_medication(db: Session, data: MedicationCreate) -> Medication:
    medication = Medication(**data.model_dump())
    db.add(medication)
    db.commit()
    db.refresh(medication)
    return medication


def get_medication(db: Session, medication_id: int) -> Medication:
    medication = db.get(Medication, medication_id)
    if medication is None:
        raise NotFoundError(f"Medication bulunamadi: {medication_id}")
    return medication


def update_medication(db: Session, medication_id: int, data: MedicationCreate) -> Medication:
    medication = get_medication(db, medication_id)
    for key, value in data.model_dump().items():
        setattr(medication, key, value)
    db.commit()
    db.refresh(medication)
    return medication


def delete_medication(db: Session, medication_id: int) -> None:
    medication = get_medication(db, medication_id)
    db.delete(medication)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu ilaç başka kayıtlar tarafından kullanıldığı için silinemez.") from exc


def list_medications(db: Session) -> list[Medication]:
    return list(db.scalars(select(Medication).order_by(Medication.name)).all())


def create_health_event(db: Session, data: HealthEventCreate) -> HealthEvent:
    event = HealthEvent(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_health_event(db: Session, event_id: int) -> HealthEvent:
    event = db.get(HealthEvent, event_id)
    if event is None:
        raise NotFoundError(f"HealthEvent bulunamadi: {event_id}")
    return event


def update_health_event(db: Session, event_id: int, data: HealthEventCreate) -> HealthEvent:
    event = get_health_event(db, event_id)
    for key, value in data.model_dump().items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


def delete_health_event(db: Session, event_id: int) -> None:
    event = get_health_event(db, event_id)
    db.delete(event)
    db.commit()


def list_health_events(db: Session, animal_id: uuid.UUID | None = None) -> list[HealthEvent]:
    stmt = select(HealthEvent)
    if animal_id is not None:
        stmt = stmt.where(HealthEvent.animal_id == animal_id)
    return list(db.scalars(stmt.order_by(HealthEvent.event_date)).all())


def calculate_withdrawal_end_date(db: Session, health_event_id: int) -> date | None:
    event = db.get(HealthEvent, health_event_id)
    if event is None or event.medication_id is None:
        return None
    medication = db.get(Medication, event.medication_id)
    if medication is None:
        return None
    return event.event_date + timedelta(days=medication.withdrawal_period_days)
