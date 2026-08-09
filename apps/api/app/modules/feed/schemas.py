from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FeedItemCreate(BaseModel):
    name: str
    feed_type_id: int
    default_unit_id: int


class FeedItemRead(FeedItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class FeedPurchaseCreate(BaseModel):
    feed_item_id: int
    purchase_date: date
    quantity: Decimal
    unit_id: int
    total_cost: Decimal | None = None
    note: str | None = None


class FeedPurchaseRead(FeedPurchaseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RationItemCreate(BaseModel):
    feed_item_id: int
    daily_quantity_per_animal: Decimal
    unit_id: int
    scope_id: int


class RationItemRead(RationItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PenRationCreate(BaseModel):
    pen_id: int
    start_date: date
    note: str | None = None
    items: list[RationItemCreate]


class PenRationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pen_id: int
    start_date: date
    end_date: date | None
    note: str | None
    items: list[RationItemRead]
    created_at: datetime
    updated_at: datetime
