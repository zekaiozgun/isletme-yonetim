"""Animal master entity (Anayasa m.7: sistemin Master Entity'si).

Diger tum modul tablolari (Weight, Breeding, Health, Feed, Pen, Sale, Death)
bu tabloya animal_id uzerinden baglanacaktir.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.date_utils import full_months_between
from app.core.orm import TimestampMixin


class Animal(TimestampMixin, Base):
    __tablename__ = "animals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Kimlik ---
    tag_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    rfid: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # --- Dogum ---
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    birth_type_id: Mapped[int | None] = mapped_column(ForeignKey("birth_types.id"), nullable=True)
    birth_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    litter_type_id: Mapped[int | None] = mapped_column(ForeignKey("litter_types.id"), nullable=True)

    # --- Soy ---
    mother_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("animals.id"), nullable=True, index=True)
    # Baba, bir Animal kaydina degil Genetic Resource modulundeki Sire (Boga)
    # katalogruna referans verir - suruye ait fiziki bogalar ile yalnizca
    # suni tohumlama icin kayitli dis kaynakli bogalar orada zaten birlikte
    # tutuluyor; bir bogayi Baba secebilmek icin ayrica tam bir Animal kaydi
    # acmaya gerek yok.
    father_sire_id: Mapped[int | None] = mapped_column(ForeignKey("sires.id"), nullable=True, index=True)
    breed_id: Mapped[int | None] = mapped_column(ForeignKey("breeds.id"), nullable=True, index=True)
    # Melez Orani: kayitli soy sertifikasindan girilen saf kan yuzdesi (orn. 87.50). Sistem hesaplamaz, fact olarak girilir.
    crossbreed_ratio: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)

    # --- Fiziksel ---
    gender_id: Mapped[int] = mapped_column(ForeignKey("genders.id"), nullable=False)
    horn_status_id: Mapped[int | None] = mapped_column(ForeignKey("horn_statuses.id"), nullable=True)

    # --- Mensei ---
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_farm_id: Mapped[int | None] = mapped_column(ForeignKey("source_farms.id"), nullable=True)
    entry_source_id: Mapped[int] = mapped_column(ForeignKey("entry_sources.id"), nullable=False)

    # --- Statu ---
    # Bu alanlar guncel/anlik durumu tutar; olay gecmisi ileride Sale/Death
    # modulleri altinda ayri Event kayitlari olarak tutulacaktir (Anayasa m.8).
    status_id: Mapped[int] = mapped_column(ForeignKey("animal_statuses.id"), nullable=False, index=True)
    status_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    death_reason_id: Mapped[int | None] = mapped_column(ForeignKey("death_reasons.id"), nullable=True)

    # --- Not (Anayasa m.6: serbest metnin izinli oldugu tek alan turu) ---
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Calisan rolundeki bir kullanici cift onayla kayit olusturdugunda true
    # olur; bu durumda kayit Calisan tarafindan bir daha PUT/DELETE ile
    # degistirilemez (YONETICI icin kisitlama yoktur). Duzeltme yolu
    # cancel-entry endpoint'i ile "Hatali Giris Iptali" statusune gecistir.
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    mother = relationship("Animal", remote_side=[id], foreign_keys=[mother_id])
    father_sire = relationship("Sire", foreign_keys=[father_sire_id])
    breed = relationship("Breed")
    gender = relationship("Gender")
    birth_type = relationship("BirthType")
    litter_type = relationship("LitterType")
    horn_status = relationship("HornStatus")
    source_farm = relationship("SourceFarm")
    entry_source = relationship("EntrySource")
    status = relationship("AnimalStatus")
    death_reason = relationship("DeathReason")

    @property
    def age_months(self) -> int | None:
        """Anayasa m.4/m.5: yas hicbir yerde saklanmaz, birth_date'ten turetilir."""
        if self.birth_date is None:
            return None
        return full_months_between(self.birth_date, date.today())
