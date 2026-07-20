"""Breeding servis katmani.

Tahmini dogum tarihi (expected calving date) DB'de saklanmaz; service_date
+ sigirda ortalama gebelik suresi (283 gun) ile burada hesaplanir
(Anayasa m.4/m.5).
"""

import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.breeding.models import BreedingEvent, PregnancyCheck
from app.modules.breeding.schemas import BreedingEventCreate, PregnancyCheckCreate

AVERAGE_GESTATION_DAYS = 283


def create_breeding_event(db: Session, data: BreedingEventCreate) -> BreedingEvent:
    event = BreedingEvent(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_breeding_event(db: Session, event_id: int) -> BreedingEvent:
    event = db.get(BreedingEvent, event_id)
    if event is None:
        raise NotFoundError(f"BreedingEvent bulunamadi: {event_id}")
    return event


def update_breeding_event(db: Session, event_id: int, data: BreedingEventCreate) -> BreedingEvent:
    event = get_breeding_event(db, event_id)
    for key, value in data.model_dump().items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


def delete_breeding_event(db: Session, event_id: int) -> None:
    event = get_breeding_event(db, event_id)
    db.delete(event)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu aşım kaydı (gebelik kontrolleri var) silinemez.") from exc


def list_breeding_events(db: Session, dam_id: uuid.UUID | None = None) -> list[BreedingEvent]:
    stmt = select(BreedingEvent)
    if dam_id is not None:
        stmt = stmt.where(BreedingEvent.dam_id == dam_id)
    return list(db.scalars(stmt.order_by(BreedingEvent.service_date)).all())


def calculate_expected_calving_date(service_date: date) -> date:
    return service_date + timedelta(days=AVERAGE_GESTATION_DAYS)


def create_pregnancy_check(db: Session, data: PregnancyCheckCreate) -> PregnancyCheck:
    check = PregnancyCheck(**data.model_dump())
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


def get_pregnancy_check(db: Session, check_id: int) -> PregnancyCheck:
    check = db.get(PregnancyCheck, check_id)
    if check is None:
        raise NotFoundError(f"PregnancyCheck bulunamadi: {check_id}")
    return check


def update_pregnancy_check(db: Session, check_id: int, data: PregnancyCheckCreate) -> PregnancyCheck:
    check = get_pregnancy_check(db, check_id)
    for key, value in data.model_dump().items():
        setattr(check, key, value)
    db.commit()
    db.refresh(check)
    return check


def delete_pregnancy_check(db: Session, check_id: int) -> None:
    check = get_pregnancy_check(db, check_id)
    db.delete(check)
    db.commit()


def list_pregnancy_checks(db: Session, breeding_event_id: int | None = None) -> list[PregnancyCheck]:
    stmt = select(PregnancyCheck)
    if breeding_event_id is not None:
        stmt = stmt.where(PregnancyCheck.breeding_event_id == breeding_event_id)
    return list(db.scalars(stmt.order_by(PregnancyCheck.check_date)).all())
