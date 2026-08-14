import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SireCreate(BaseModel):
    registry_no: str | None = None
    name: str
    breed_id: int
    animal_id: uuid.UUID | None = None
    is_external: bool = True
    # Sadece dis kaynakli (is_external=True) bogalarda anlamli - bkz.
    # models.py Sire dokstringi. Suruye ait bir bogada (animal_id dolu)
    # bu alanlar kullanilmaz, o boganin kendi soy agaci zaten Animal
    # kaydindan turetilir.
    known_sire_registry_no: str | None = None
    known_sire_name: str | None = None
    known_dam_registry_no: str | None = None
    known_dam_name: str | None = None
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
