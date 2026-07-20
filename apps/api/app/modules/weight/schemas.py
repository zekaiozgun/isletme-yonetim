import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class WeightRecordCreate(BaseModel):
    animal_id: uuid.UUID
    weigh_date: date
    weight_kg: Decimal
    weighing_method_id: int
    note: str | None = None


class WeightRecordRead(WeightRecordCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
