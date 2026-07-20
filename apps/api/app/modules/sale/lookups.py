"""Master Data (lookup) tables for the Sale bounded context."""

from app.core.database import Base
from app.core.orm import LookupMixin


class SaleType(LookupMixin, Base):
    """Satis Tipi (Canli Satis, Kesim Icin Satis, Damizlik Satis)."""

    __tablename__ = "sale_types"
