import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SireCreate(BaseModel):
    registry_no: str | None = None
    name: str
    breed_id: int
    animal_id: uuid.UUID | None = None
    is_external: bool = True
    note: str | None = None


class SireRead(SireCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SemenBatchCreate(BaseModel):
    sire_id: int
    batch_no: str
    supplier_farm_id: int | None = None
    purchase_date: date
    straw_count: int
    storage_location: str | None = None
    note: str | None = None


class SemenBatchRead(SemenBatchCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
