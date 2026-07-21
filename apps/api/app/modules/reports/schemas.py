"""Raporlama (analiz) katmani sema tanimlari.

Anayasa m.2: Veri Girisi ile Analiz/Raporlama kesin olarak ayrilir. Bu
semalar hicbir ORM modeline (Create/Read ciftine) karsilik gelmez; servis
katmaninda birden fazla modul (Animal, Breeding, Pen) birlestirilerek elle
insa edilen, salt-okunur turetilmis goruntulerdir (Anayasa m.4/m.5).
"""

import uuid
from datetime import date

from pydantic import BaseModel


class BreedingCandidateRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    birth_date: date | None = None
    age_months: int | None = None
    reason: str
    last_calving_date: date | None = None
    last_service_date: date | None = None


class BredAnimalRead(BaseModel):
    breeding_event_id: int
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    service_date: date
    service_method_name: str
    days_since_service: int
    check_status: str
    pregnancy_check_due: bool
    expected_calving_date: date | None = None


class RepeatBreederRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    last_service_date: date
    days_open: int
    service_method_name: str


class PregnantAnimalRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    service_date: date
    expected_calving_date: date
    days_until_calving: int


class YoungAnimalRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    gender_name: str
    birth_date: date | None = None
    age_months: int | None = None
    age_days: int | None = None
    mother_tag_number: str | None = None


class PenOccupancyRead(BaseModel):
    pen_id: int
    code: str
    name: str
    capacity: int | None = None
    current_count: int
    occupancy_rate: float | None = None


class HerdInventoryRead(BaseModel):
    total_active: int
    by_status: dict[str, int]
    female_active: int
    male_active: int
    calves_count: int
    heifers_steers_count: int
    breeding_age_female_count: int
    adult_male_count: int


class DashboardSummaryRead(BaseModel):
    active_animal_count: int
    breeding_candidate_count: int
    pregnancy_check_due_count: int
    pregnant_count: int
    repeat_breeder_count: int
    calves_count: int
    heifers_steers_count: int
    pen_occupancy_rate: float | None = None
