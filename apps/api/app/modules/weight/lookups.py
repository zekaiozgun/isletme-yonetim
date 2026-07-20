"""Master Data (lookup) tables for the Weight bounded context."""

from app.core.database import Base
from app.core.orm import LookupMixin


class WeighingMethod(LookupMixin, Base):
    """Tarti Yontemi (Dijital Kantar, Elle Tarti, Bant Olcumu / Tahmini)."""

    __tablename__ = "weighing_methods"
