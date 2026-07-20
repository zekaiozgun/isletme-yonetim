"""Master Data (lookup) tables for the Feed bounded context."""

from app.core.database import Base
from app.core.orm import LookupMixin


class FeedType(LookupMixin, Base):
    """Yem Tipi (Kaba Yem, Kesif Yem, Silaj, Mineral/Vitamin)."""

    __tablename__ = "feed_types"


class FeedUnit(LookupMixin, Base):
    """Yem Birimi (kg, ton)."""

    __tablename__ = "feed_units"
