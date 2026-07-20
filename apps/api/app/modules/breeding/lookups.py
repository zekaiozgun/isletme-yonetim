"""Master Data (lookup) tables for the Breeding bounded context."""

from app.core.database import Base
from app.core.orm import LookupMixin


class ServiceMethod(LookupMixin, Base):
    """Astirma Yontemi (Dogal Asim, Suni Tohumlama, Embriyo Transferi)."""

    __tablename__ = "service_methods"


class PregnancyCheckMethod(LookupMixin, Base):
    """Gebelik Kontrol Yontemi (Rektal Muayene, Ultrason, Kan Testi)."""

    __tablename__ = "pregnancy_check_methods"


class PregnancyResult(LookupMixin, Base):
    """Gebelik Kontrol Sonucu (Gebe, Bos, Supheli)."""

    __tablename__ = "pregnancy_results"
