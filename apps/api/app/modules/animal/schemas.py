"""Pydantic schemas: veri girisi (Create) ile okuma (Read) sozlesmeleri
kesin olarak ayrilir (Anayasa m.2). Create semasi yalnizca kullanicinin
girebilecegi gercek olaylari (facts) icerir; hesaplanabilir hicbir alan
(orn. yas, gunluk canli agirlik artisi) burada yer almaz (Anayasa m.4).

status_id/status_date/death_reason_id, AnimalCreate'te YOKTUR: yeni
kaydedilen bir hayvan her zaman "Aktif" statusuyle baslar (service
katmani tarafindan otomatik atanir). Bu alanlar yalnizca Sale/Death
modullerinin ilgili event'leri olusturmasiyla degisir (Anayasa m.8).
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AnimalBase(BaseModel):
    tag_number: str
    rfid: str | None = None
    name: str | None = None

    birth_date: date | None = None
    birth_type_id: int | None = None
    birth_weight_kg: Decimal | None = None
    litter_type_id: int | None = None

    mother_id: uuid.UUID | None = None
    father_sire_id: int | None = None
    breed_id: int | None = None
    crossbreed_ratio: Decimal | None = None

    gender_id: int
    horn_status_id: int | None = None

    entry_date: date
    source_farm_id: int | None = None
    entry_source_id: int
    entry_value: Decimal | None = None

    note: str | None = None


class AnimalCreate(AnimalBase):
    pass


class AnimalRead(AnimalBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status_id: int
    status_date: date | None = None
    death_reason_id: int | None = None
    age_months: int | None = None
    is_locked: bool
    created_at: datetime
    updated_at: datetime


class AnimalCancelEntry(BaseModel):
    """'Hatalı Giriş İptali' istegi: sadece opsiyonel bir aciklama."""

    note: str | None = None
