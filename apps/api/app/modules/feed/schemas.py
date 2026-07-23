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


class FeedDistributionCreate(BaseModel):
    pen_id: int
    feed_item_id: int
    distribution_date: date
    quantity: Decimal
    unit_id: int
    total_cost: Decimal | None = None
    note: str | None = None


class FeedDistributionRead(FeedDistributionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
