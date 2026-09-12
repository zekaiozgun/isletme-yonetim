import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator


class SireCreate(BaseModel):
    registry_no: str | None = None
    # Sadece animal_id BOŞSA (dış kaynaklı boğa) zorunludur - sürüye ait
    # bir boğada (animal_id dolu) kimlik Animal kaydından gelir, burada
    # ayrıca istenmez (bkz. models.py Sire.display_name).
    name: str | None = None
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

    @model_validator(mode="after")
    def _require_name_when_not_herd_linked(self) -> "SireCreate":
        if self.animal_id is None and not (self.name or "").strip():
            raise ValueError("Sürüde kayıtlı bir hayvan seçilmediyse Ad alanı zorunludur.")
        return self


class SireRead(SireCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str
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
