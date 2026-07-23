"""Genetic Resource: sire (boga) kaydi ve sperma/straw stok takibi.

breeds (Animal modulunden) ve source_farms (tedarikci isletme, Animal
modulunden) burada yeniden kullanilir - Anayasa m.6 geregi ayni kavram
icin ikinci bir lookup tablosu acilmaz.
"""

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class Sire(TimestampMixin, Base):
    """Boga kaydi - suruye ait olabilir (animal_id dolu) ya da disaridan (is_external)."""

    __tablename__ = "sires"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    registry_no: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    breed_id: Mapped[int] = mapped_column(ForeignKey("breeds.id"), nullable=False)
    animal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=True, unique=True
    )
    is_external: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    breed = relationship("Breed")
    # foreign_keys gerekli: animals.father_sire_id de sires.id'ye referans
    # veriyor, iki tablo arasinda birden fazla FK yolu var (belirsizligi
    # gidermek icin bu iliskinin hangi sutunu kullandigini acikca belirtiyoruz).
    animal = relationship("Animal", foreign_keys=[animal_id])


class SemenBatch(TimestampMixin, Base):
    """Sperma/straw stok partisi (bir boganin belirli bir alim lotu)."""

    __tablename__ = "semen_batches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sire_id: Mapped[int] = mapped_column(ForeignKey("sires.id"), nullable=False, index=True)
    batch_no: Mapped[str] = mapped_column(String(64), nullable=False)
    supplier_farm_id: Mapped[int | None] = mapped_column(ForeignKey("source_farms.id"), nullable=True)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    straw_count: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    sire = relationship("Sire")
    supplier_farm = relationship("SourceFarm")

    __table_args__ = (UniqueConstraint("sire_id", "batch_no", name="uq_semen_batches_sire_batch_no"),)
