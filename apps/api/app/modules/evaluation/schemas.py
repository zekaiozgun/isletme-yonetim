import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EvaluationReasonCreate(BaseModel):
    code: str
    name: str
    direction_id: int
    is_active: bool = True


class EvaluationReasonRead(EvaluationReasonCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class AnimalEvaluationCreate(BaseModel):
    animal_id: uuid.UUID
    evaluation_date: date
    reason_id: int
    priority_id: int | None = None
    note: str | None = None


class AnimalEvaluationRead(AnimalEvaluationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
