import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DeathCreate(BaseModel):
    animal_id: uuid.UUID
    death_date: date
    death_reason_id: int
    disposal_method_id: int
    necropsy_performed: bool = False
    note: str | None = None


class DeathRead(DeathCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
