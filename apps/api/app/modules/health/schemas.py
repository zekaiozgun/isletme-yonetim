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


class HealthEventMedicationInput(BaseModel):
    medication_id: int
    dosage_amount: Decimal | None = None
    dosage_unit_id: int | None = None


class HealthEventMedicationRead(HealthEventMedicationInput):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medication_name: str
    dosage_unit_name: str | None = None


class HealthEventCreate(BaseModel):
    animal_id: uuid.UUID
    event_type_id: int
    event_date: date
    disease_id: int | None = None
    medications: list[HealthEventMedicationInput] = []
    veterinarian_note: str | None = None
    cost: Decimal | None = None
    note: str | None = None


class HealthEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal_id: uuid.UUID
    event_type_id: int
    event_date: date
    disease_id: int | None = None
    medications: list[HealthEventMedicationRead] = []
    veterinarian_note: str | None = None
    cost: Decimal | None = None
    note: str | None = None
    created_at: datetime
    updated_at: datetime
