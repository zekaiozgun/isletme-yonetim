"""Weight records: append-only tarti olaylari (Anayasa m.8).

Gunluk canli agirlik artisi (ADG) gibi turevler burada saklanmaz; servis
katmani iki weight_records kaydi arasindan hesaplar (Anayasa m.4/m.5).
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class WeightRecord(TimestampMixin, Base):
    __tablename__ = "weight_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    animal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, index=True)
    weigh_date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    weighing_method_id: Mapped[int] = mapped_column(ForeignKey("weighing_methods.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    animal = relationship("Animal")
    weighing_method = relationship("WeighingMethod")
