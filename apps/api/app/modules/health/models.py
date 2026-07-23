"""Health: ilac/asi master verisi ve saglik olay gunlugu.

withdrawal_period_days ilaca ait bir fact'tir (uretici tarafindan
belirlenir); withdrawal_end_date her olayda ayrica saklanmaz, servis
katmaninda event_date + medication.withdrawal_period_days olarak
hesaplanir (Anayasa m.4/m.5).
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class Medication(TimestampMixin, Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    active_ingredient: Mapped[str | None] = mapped_column(String(120), nullable=True)
    medication_type_id: Mapped[int] = mapped_column(ForeignKey("medication_types.id"), nullable=False)
    withdrawal_period_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    medication_type = relationship("MedicationType")


class HealthEvent(TimestampMixin, Base):
    __tablename__ = "health_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    animal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, index=True)
    event_type_id: Mapped[int] = mapped_column(ForeignKey("health_event_types.id"), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    disease_id: Mapped[int | None] = mapped_column(ForeignKey("diseases.id"), nullable=True)
    medication_id: Mapped[int | None] = mapped_column(ForeignKey("medications.id"), nullable=True)
    dosage_amount: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    dosage_unit_id: Mapped[int | None] = mapped_column(ForeignKey("dosage_units.id"), nullable=True)
    veterinarian_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Bu olayin toplam maliyeti (ilac + varsa veteriner ucreti dahil tek tutar, TL).
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    animal = relationship("Animal")
    event_type = relationship("HealthEventType")
    disease = relationship("Disease")
    medication = relationship("Medication")
    dosage_unit = relationship("DosageUnit")
