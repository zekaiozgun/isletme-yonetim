"""Breeding servis katmani.

Tahmini dogum tarihi (expected calving date) DB'de saklanmaz; service_date
+ sigirda ortalama gebelik suresi (283 gun) ile burada hesaplanir
(Anayasa m.4/m.5).
"""

import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.date_utils import add_months
from app.core.exceptions import ConflictError, DomainError, NotFoundError
from app.core.validators import require_date_order
from app.modules.animal import service as animal_service
from app.modules.animal.models import Animal
from app.modules.breeding.models import BreedingEvent, PregnancyCheck
from app.modules.breeding.schemas import BreedingEventCreate, InbreedingCheckRead, PregnancyCheckCreate
from app.modules.genetic_resource.models import SemenBatch

AVERAGE_GESTATION_DAYS = 283
# Boğanın cinsel olgunluğa erişip damızlıkta fiilen kullanılabildiği asgari
# yaş - sadece "doğmuş olması" yeterli degil (bkz. _validate_breeding_event_dates).
MIN_SIRE_BREEDING_AGE_MONTHS = 11


def _validate_breeding_event_dates(db: Session, event: BreedingEvent) -> None:
    dam = db.get(Animal, event.dam_id)
    if dam is not None:
        require_date_order(dam.birth_date, "İneğin doğum tarihi", event.service_date, "Tohumlama tarihi")
    if event.sire_animal_id is not None:
        sire = db.get(Animal, event.sire_animal_id)
        if sire is not None and sire.birth_date is not None:
            min_breeding_date = add_months(sire.birth_date, MIN_SIRE_BREEDING_AGE_MONTHS)
            if event.service_date < min_breeding_date:
                raise DomainError(
                    f"Boğa, tohumlama tarihinde ({event.service_date.isoformat()}) henüz "
                    f"{MIN_SIRE_BREEDING_AGE_MONTHS} aylık damızlık yaşına ulaşmamış "
                    f"(doğum: {sire.birth_date.isoformat()}, en erken tohumlama tarihi: "
                    f"{min_breeding_date.isoformat()})."
                )


def create_breeding_event(db: Session, data: BreedingEventCreate) -> BreedingEvent:
    event = BreedingEvent(**data.model_dump())
    _validate_breeding_event_dates(db, event)
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
    _validate_breeding_event_dates(db, event)
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


def list_breeding_events(
    db: Session, dam_id: uuid.UUID | None = None, pending_check: bool | None = None
) -> list[BreedingEvent]:
    stmt = select(BreedingEvent).options(joinedload(BreedingEvent.dam))
    if dam_id is not None:
        stmt = stmt.where(BreedingEvent.dam_id == dam_id)
    if pending_check:
        # Sahada gebelik kontrolu girilirken, tohumlamasi yapilip henuz
        # kontrol edilmemis hayvanlari pulldown'da listeleyebilmek icin:
        # kendisine bagli hic pregnancy_checks kaydi olmayan asim kayitlari.
        has_check = (
            select(PregnancyCheck.id)
            .where(PregnancyCheck.breeding_event_id == BreedingEvent.id)
            .exists()
        )
        stmt = stmt.where(~has_check)
    return list(db.scalars(stmt.order_by(BreedingEvent.service_date)).all())


def calculate_expected_calving_date(service_date: date) -> date:
    return service_date + timedelta(days=AVERAGE_GESTATION_DAYS)


def _validate_pregnancy_check_date(db: Session, check: PregnancyCheck) -> None:
    event = db.get(BreedingEvent, check.breeding_event_id)
    if event is not None:
        require_date_order(event.service_date, "Tohumlama tarihi", check.check_date, "Gebelik kontrol tarihi")


def create_pregnancy_check(db: Session, data: PregnancyCheckCreate) -> PregnancyCheck:
    check = PregnancyCheck(**data.model_dump())
    _validate_pregnancy_check_date(db, check)
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
    _validate_pregnancy_check_date(db, check)
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


INBREEDING_CHECK_GENERATIONS = 4


def check_inbreeding(
    db: Session, dam_id: uuid.UUID | None, sire_animal_id: uuid.UUID | None, semen_batch_id: int | None
) -> InbreedingCheckRead:
    """Anne adayi ile prospektif boganin (dogal asim -> sire_animal_id,
    suni tohumlama -> semen_batch_id uzerinden Sire) soy agaclarinda
    (bkz. animal/service.py get_pedigree_tree) ORTAK bir ata olup
    olmadigini kontrol eder - formu ENGELLEMEZ, sadece kullaniciyi
    bilgilendirir (kullanicinin onayladigi kural seti, Faz 4)."""
    no_match = InbreedingCheckRead(has_common_ancestor=False, common_ancestor_names=[])
    if dam_id is None:
        return no_match

    dam_tree = animal_service.get_pedigree_tree(db, dam_id, INBREEDING_CHECK_GENERATIONS)

    if sire_animal_id is not None:
        sire_tree = animal_service.get_pedigree_tree(db, sire_animal_id, INBREEDING_CHECK_GENERATIONS)
    elif semen_batch_id is not None:
        batch = db.get(SemenBatch, semen_batch_id)
        if batch is None:
            return no_match
        sire_tree = animal_service.build_pedigree_tree_for_sire_id(db, batch.sire_id, INBREEDING_CHECK_GENERATIONS)
        if sire_tree is None:
            return no_match
    else:
        return no_match

    common = animal_service.find_common_ancestors(dam_tree, sire_tree)
    return InbreedingCheckRead(has_common_ancestor=len(common) > 0, common_ancestor_names=common)
