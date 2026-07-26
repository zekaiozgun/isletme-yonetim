from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class GrowthValuationCheckpointCreate(BaseModel):
    gender_id: int
    # Yalnizca bu dort yas noktasi desteklenir (bkz. models.py CheckConstraint) -
    # Literal ile burada reddedilir, DB'ye kadar gidip belirsiz bir
    # IntegrityError/ConflictError'a donusmez.
    age_months: Literal[3, 6, 9, 12]
    value_usd: Decimal


class GrowthValuationCheckpointRead(GrowthValuationCheckpointCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
