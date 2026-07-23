"""Animal servis katmani: veri girisi + Anayasa m.4/m.5 geregi turetilen
degerler (yas gibi) burada hesaplanir, hicbir zaman DB'de saklanmaz."""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.lookup_helpers import get_lookup_by_code
from app.modules.animal.lookups import AnimalStatus
from app.modules.animal.models import Animal
from app.modules.animal.schemas import AnimalCreate
from app.modules.auth.schemas import Role

ACTIVE_STATUS_CODE = "AKTIF"
CANCELLED_ENTRY_STATUS_CODE = "HATALI_GIRIS"


def create_animal(db: Session, data: AnimalCreate, created_by_role: Role) -> Animal:
    """Calisan rolu, kaydi cift-onay akisindan gecirdigi icin otomatik
    kilitli (is_locked=True) olusturur - bkz. update_animal."""
    active_status = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE)
    animal = Animal(
        **data.model_dump(),
        status_id=active_status.id,
        status_date=None,
        death_reason_id=None,
        is_locked=(created_by_role == "CALISAN"),
    )
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal


def get_animal(db: Session, animal_id: uuid.UUID) -> Animal:
    animal = db.get(Animal, animal_id)
    if animal is None:
        raise NotFoundError(f"Animal bulunamadi: {animal_id}")
    return animal


def update_animal(db: Session, animal_id: uuid.UUID, data: AnimalCreate, requester_role: Role) -> Animal:
    """status_id/status_date/death_reason_id AnimalCreate'te olmadigi icin
    guncellemez - bu alanlar yalnizca Sale/Death event'leriyle degisir.

    Kayit is_locked ise (Calisan'in cift onayla olusturdugu bir kayit),
    yalnizca YONETICI degistirebilir - Calisan icin 409 doner. Duzeltme
    yolu cancel_animal_entry (Hatali Giris Iptali)."""
    animal = get_animal(db, animal_id)
    if animal.is_locked and requester_role != "YONETICI":
        raise ConflictError(
            "Bu hayvan kaydı onaylanmış ve kilitlenmiş; değiştirilemez. "
            "Hatalı giriş ise 'Hatalı Giriş İptali' ile pasife alın."
        )
    for key, value in data.model_dump().items():
        setattr(animal, key, value)
    db.commit()
    db.refresh(animal)
    return animal


def cancel_animal_entry(db: Session, animal_id: uuid.UUID, note: str | None = None) -> Animal:
    """'Hatalı Giriş İptali': hem Çalışan hem Yönetici kullanabilir -
    is_locked kontrolü BİLEREK yapılmaz, kilitli bir kaydı düzeltmenin tek
    yolu budur. Sale/Death gibi Animal.status'u değiştiren ayrı bir 'event'
    işlemidir (Anayasa m.8), PUT ile karıştırılmamalı."""
    animal = get_animal(db, animal_id)
    cancelled_status = get_lookup_by_code(db, AnimalStatus, CANCELLED_ENTRY_STATUS_CODE)
    animal.status_id = cancelled_status.id
    animal.status_date = date.today()
    if note:
        animal.note = note
    db.commit()
    db.refresh(animal)
    return animal


def delete_animal(db: Session, animal_id: uuid.UUID) -> None:
    animal = get_animal(db, animal_id)
    db.delete(animal)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu hayvan başka kayıtlar (tartı, sağlık, satış, soy vb.) tarafından kullanıldığı için silinemez.") from exc


def list_animals(db: Session, status_id: int | None = None) -> list[Animal]:
    stmt = select(Animal)
    if status_id is not None:
        stmt = stmt.where(Animal.status_id == status_id)
    return list(db.scalars(stmt.order_by(Animal.tag_number)).all())


def calculate_age_in_days(animal: Animal, as_of: date | None = None) -> int | None:
    """Yas, birth_date'ten turetilir; DB'de saklanmaz (Anayasa m.4/m.5)."""
    if animal.birth_date is None:
        return None
    reference_date = as_of or date.today()
    return (reference_date - animal.birth_date).days
