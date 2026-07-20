from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.genetic_resource.models import SemenBatch, Sire
from app.modules.genetic_resource.schemas import SemenBatchCreate, SireCreate


def create_sire(db: Session, data: SireCreate) -> Sire:
    sire = Sire(**data.model_dump())
    db.add(sire)
    db.commit()
    db.refresh(sire)
    return sire


def get_sire(db: Session, sire_id: int) -> Sire:
    sire = db.get(Sire, sire_id)
    if sire is None:
        raise NotFoundError(f"Sire bulunamadi: {sire_id}")
    return sire


def update_sire(db: Session, sire_id: int, data: SireCreate) -> Sire:
    sire = get_sire(db, sire_id)
    for key, value in data.model_dump().items():
        setattr(sire, key, value)
    db.commit()
    db.refresh(sire)
    return sire


def delete_sire(db: Session, sire_id: int) -> None:
    sire = get_sire(db, sire_id)
    db.delete(sire)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu boğa başka kayıtlar tarafından kullanıldığı için silinemez.") from exc


def list_sires(db: Session) -> list[Sire]:
    return list(db.scalars(select(Sire).order_by(Sire.name)).all())


def create_semen_batch(db: Session, data: SemenBatchCreate) -> SemenBatch:
    batch = SemenBatch(**data.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def get_semen_batch(db: Session, batch_id: int) -> SemenBatch:
    batch = db.get(SemenBatch, batch_id)
    if batch is None:
        raise NotFoundError(f"SemenBatch bulunamadi: {batch_id}")
    return batch


def update_semen_batch(db: Session, batch_id: int, data: SemenBatchCreate) -> SemenBatch:
    batch = get_semen_batch(db, batch_id)
    for key, value in data.model_dump().items():
        setattr(batch, key, value)
    db.commit()
    db.refresh(batch)
    return batch


def delete_semen_batch(db: Session, batch_id: int) -> None:
    batch = get_semen_batch(db, batch_id)
    db.delete(batch)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu sperma partisi başka kayıtlar tarafından kullanıldığı için silinemez.") from exc


def list_semen_batches(db: Session, sire_id: int | None = None) -> list[SemenBatch]:
    stmt = select(SemenBatch)
    if sire_id is not None:
        stmt = stmt.where(SemenBatch.sire_id == sire_id)
    return list(db.scalars(stmt.order_by(SemenBatch.purchase_date)).all())
