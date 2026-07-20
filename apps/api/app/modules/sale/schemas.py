import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BuyerCreate(BaseModel):
    name: str
    phone: str | None = None
    tax_no: str | None = None
    address: str | None = None
    note: str | None = None


class BuyerRead(BuyerCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SaleCreate(BaseModel):
    animal_id: uuid.UUID
    sale_date: date
    buyer_id: int
    sale_type_id: int
    sale_weight_kg: Decimal | None = None
    total_amount: Decimal
    note: str | None = None


class SaleRead(SaleCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
