"""Master Data (lookup) tables for the Pen bounded context."""

from app.core.database import Base
from app.core.orm import LookupMixin


class PenType(LookupMixin, Base):
    """Padok Tipi (orn. Dogum Padoku, Besi Padoku, Karantina, Hastane Padogu)."""

    __tablename__ = "pen_types"


class PenAssignmentReason(LookupMixin, Base):
    """Padok Degisim Nedeni (orn. Buyume, Saglik, Cinsiyet Ayrimi, Dogum)."""

    __tablename__ = "pen_assignment_reasons"
