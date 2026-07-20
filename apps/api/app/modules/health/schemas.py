import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MedicationCreate(BaseModel):
    name: str
    active_ingredient: str | None = None
    medication_type_id: int
    withdrawal_period_days: int = 0


class MedicationRead(MedicationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class HealthEventCreate(BaseModel):
    animal_id: uuid.UUID
    event_type_id: int
    event_date: date
    disease_id: int | None = None
    medication_id: int | None = None
    dosage_amount: Decimal | None = None
    dosage_unit_id: int | None = None
    veterinarian_note: str | None = None
    note: str | None = None


class HealthEventRead(HealthEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
