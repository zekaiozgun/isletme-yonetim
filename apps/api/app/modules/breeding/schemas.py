import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator


class BreedingEventCreate(BaseModel):
    dam_id: uuid.UUID
    service_method_id: int
    service_date: date
    sire_animal_id: uuid.UUID | None = None
    semen_batch_id: int | None = None
    note: str | None = None

    @model_validator(mode="after")
    def validate_exactly_one_sire_source(self) -> "BreedingEventCreate":
        if (self.sire_animal_id is None) == (self.semen_batch_id is None):
            raise ValueError("sire_animal_id ve semen_batch_id alanlarindan tam olarak biri dolu olmalidir")
        return self


class BreedingEventRead(BreedingEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dam_tag_number: str | None = None
    created_at: datetime
    updated_at: datetime


class PregnancyCheckCreate(BaseModel):
    breeding_event_id: int
    check_date: date
    method_id: int
    result_id: int
    note: str | None = None


class PregnancyCheckRead(PregnancyCheckCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
