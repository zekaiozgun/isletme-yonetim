"""Master Data (lookup) tables for the Health bounded context."""

from app.core.database import Base
from app.core.orm import LookupMixin


class HealthEventType(LookupMixin, Base):
    """Saglik Olayi Tipi (Asilama, Tedavi, Muayene, Hastalik Bildirimi)."""

    __tablename__ = "health_event_types"


class Disease(LookupMixin, Base):
    """Hastalik/Tani (orn. Sap-Tirnak, Solunum Yolu Enfeksiyonu)."""

    __tablename__ = "diseases"


class MedicationType(LookupMixin, Base):
    """Ilac Tipi (Asi, Antibiyotik, Parazit Ilaci, Vitamin/Mineral, Diger)."""

    __tablename__ = "medication_types"


class DosageUnit(LookupMixin, Base):
    """Doz Birimi (ml, mg, cc, doz)."""

    __tablename__ = "dosage_units"
