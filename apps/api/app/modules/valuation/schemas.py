from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

CategoryCode = Literal["AGE_3", "AGE_6", "AGE_9", "AGE_12", "GEBE", "BOS"]


class GrowthValuationCheckpointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    gender_id: int
    category_code: CategoryCode
    value_try: Decimal
    created_at: datetime
    updated_at: datetime


class GrowthValuationCheckpointItem(BaseModel):
    gender_id: int
    category_code: CategoryCode
    # None ise (kullanıcı tablo hücresini boş bıraktıysa) bu satır - varsa -
    # silinir; dolu bir değer ise oluşturulur/güncellenir (bkz. service.py
    # replace_checkpoints - "tablodaki ne görünüyorsa o kaydedilir" semantiği).
    value_try: Decimal | None = None


class GrowthValuationCheckpointBulkUpdate(BaseModel):
    items: list[GrowthValuationCheckpointItem]
