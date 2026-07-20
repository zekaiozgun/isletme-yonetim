"""Master Data (lookup) tables for the Animal bounded context.

Anayasa m.6: Serbest metin yalnizca Not/Aciklama alanlarinda kullanilir;
asagidaki her alan Animal tablosunda FK olarak referans verilen, kendi
basina yonetilebilir bir Master Data tablosudur.
"""

from app.core.database import Base
from app.core.orm import LookupMixin


class Breed(LookupMixin, Base):
    """Irk (orn. Simental, Sarole, Angus)."""

    __tablename__ = "breeds"


class Gender(LookupMixin, Base):
    """Cinsiyet (Erkek / Disi)."""

    __tablename__ = "genders"


class BirthType(LookupMixin, Base):
    """Dogum Sekli (orn. Normal Dogum, Sezaryen, Guc Dogum)."""

    __tablename__ = "birth_types"


class LitterType(LookupMixin, Base):
    """Dogum Tipi (Tekiz / Ikiz / Ucuz)."""

    __tablename__ = "litter_types"


class HornStatus(LookupMixin, Base):
    """Boynuz Durumu (Boynuzlu / Boynuzsuz / Boynuzu Alinmis)."""

    __tablename__ = "horn_statuses"


class SourceFarm(LookupMixin, Base):
    """Gelinen Isletme (disaridan gelen hayvanin kaynak isletmesi)."""

    __tablename__ = "source_farms"


class EntrySource(LookupMixin, Base):
    """Giris Kaynagi (orn. Isletmede Dogum, Satin Alma, Devir)."""

    __tablename__ = "entry_sources"


class AnimalStatus(LookupMixin, Base):
    """Statu (Aktif / Satildi / Oldu / Kesildi)."""

    __tablename__ = "animal_statuses"


class DeathReason(LookupMixin, Base):
    """Olum Nedeni (orn. Hastalik, Kaza, Bilinmeyen)."""

    __tablename__ = "death_reasons"
