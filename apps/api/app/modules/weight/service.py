"""Weight servis katmani.

Gunluk canli agirlik artisi (ADG - Average Daily Gain) DB'de saklanmaz;
en son iki tarti kaydi arasindan burada hesaplanir (Anayasa m.4/m.5).
"""

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.weight.models import WeightRecord
from app.modules.weight.schemas import WeightRecordCreate


def create_weight_record(db: Session, data: WeightRecordCreate) -> WeightRecord:
    record = WeightRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_weight_record(db: Session, record_id: int) -> WeightRecord:
    record = db.get(WeightRecord, record_id)
    if record is None:
        raise NotFoundError(f"WeightRecord bulunamadi: {record_id}")
    return record


def update_weight_record(db: Session, record_id: int, data: WeightRecordCreate) -> WeightRecord:
    record = get_weight_record(db, record_id)
    for key, value in data.model_dump().items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_weight_record(db: Session, record_id: int) -> None:
    record = get_weight_record(db, record_id)
    db.delete(record)
    db.commit()


def list_weight_records(db: Session, animal_id: uuid.UUID | None = None) -> list[WeightRecord]:
    stmt = select(WeightRecord)
    if animal_id is not None:
        stmt = stmt.where(WeightRecord.animal_id == animal_id)
    return list(db.scalars(stmt.order_by(WeightRecord.weigh_date)).all())


def calculate_average_daily_gain(db: Session, animal_id: uuid.UUID) -> Decimal | None:
    """Son iki tarti kaydi arasindaki gunluk ortalama agirlik artisi (kg/gun)."""
    records = list_weight_records(db, animal_id)
    if len(records) < 2:
        return None
    earlier, later = records[-2], records[-1]
    days = (later.weigh_date - earlier.weigh_date).days
    if days <= 0:
        return None
    return (later.weight_kg - earlier.weight_kg) / Decimal(days)
