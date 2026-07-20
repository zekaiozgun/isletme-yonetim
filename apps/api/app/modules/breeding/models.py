"""Breeding: astirma (service) olaylari ve gebelik kontrolleri.

Buzagilama (calving) icin ayri bir tablo yoktur - buzagi, Animal
tablosunda mother_id/father_id ve dogum alanlariyla temsil edilir
(Anayasa m.7). breeding_events sadece gebelik donemini baslatan olayi
belgeler.
"""

import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class BreedingEvent(TimestampMixin, Base):
    __tablename__ = "breeding_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dam_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, index=True)
    service_method_id: Mapped[int] = mapped_column(ForeignKey("service_methods.id"), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Tam olarak biri dolu olmalidir: dogal asim -> sire_animal_id, suni tohumlama -> semen_batch_id.
    sire_animal_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("animals.id"), nullable=True)
    semen_batch_id: Mapped[int | None] = mapped_column(ForeignKey("semen_batches.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "(sire_animal_id IS NOT NULL) <> (semen_batch_id IS NOT NULL)",
            name="ck_breeding_events_sire_xor_semen",
        ),
    )

    dam = relationship("Animal", foreign_keys=[dam_id])
    sire_animal = relationship("Animal", foreign_keys=[sire_animal_id])
    service_method = relationship("ServiceMethod")
    semen_batch = relationship("SemenBatch")


class PregnancyCheck(TimestampMixin, Base):
    __tablename__ = "pregnancy_checks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    breeding_event_id: Mapped[int] = mapped_column(ForeignKey("breeding_events.id"), nullable=False, index=True)
    check_date: Mapped[date] = mapped_column(Date, nullable=False)
    method_id: Mapped[int] = mapped_column(ForeignKey("pregnancy_check_methods.id"), nullable=False)
    result_id: Mapped[int] = mapped_column(ForeignKey("pregnancy_results.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    breeding_event = relationship("BreedingEvent")
    method = relationship("PregnancyCheckMethod")
    result = relationship("PregnancyResult")
