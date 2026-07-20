"""Master Data (lookup) tables for the Death bounded context.

death_reasons Animal modulunden yeniden kullanilir (Anayasa m.6) - burada
tekrar tanimlanmaz.
"""

from app.core.database import Base
from app.core.orm import LookupMixin


class DisposalMethod(LookupMixin, Base):
    """Imha Yontemi (Gomme, Rendering, Yakma, Diger)."""

    __tablename__ = "disposal_methods"
