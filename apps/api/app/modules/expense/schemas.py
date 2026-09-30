from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class GeneralExpenseCreate(BaseModel):
    expense_date: date
    category_id: int
    amount: Decimal
    note: str | None = None


class GeneralExpenseRead(GeneralExpenseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
