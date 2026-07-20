import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PenCreate(BaseModel):
    code: str
    name: str
    pen_type_id: int
    capacity: int | None = None
    note: str | None = None


class PenRead(PenCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PenAssignmentCreate(BaseModel):
    animal_id: uuid.UUID
    pen_id: int
    assigned_date: date
    removed_date: date | None = None
    reason_id: int
    note: str | None = None


class PenAssignmentRead(PenAssignmentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
