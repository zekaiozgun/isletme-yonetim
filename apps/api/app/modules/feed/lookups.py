"""Master Data (lookup) tables for the Feed bounded context."""

from app.core.database import Base
from app.core.orm import LookupMixin


class FeedType(LookupMixin, Base):
    """Yem Tipi (Kaba Yem, Kesif Yem, Silaj, Mineral/Vitamin)."""

    __tablename__ = "feed_types"


class FeedUnit(LookupMixin, Base):
    """Yem Birimi (kg, ton)."""

    __tablename__ = "feed_units"


class RationItemScope(LookupMixin, Base):
    """Bir rasyon kaleminin padoktaki hangi yaş grubuna uygulandığı (Tüm
    Hayvanlar / Sadece Buzağı / Sadece Yetişkin) - anne-yavru padoklarında
    buzağıların yetişkinlerle homojen sayılmasını (tam porsiyon yiyormuş
    gibi) önlemek için (bkz. reports/service.py)."""

    __tablename__ = "ration_item_scopes"
