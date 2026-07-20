"""Feed: yem urunu master verisi ve padok bazinda yem dagitim gunlugu.

V1 kapsaminda yem, bireysel hayvana degil pen'e (padok/grup) dagitilir;
rasyon/recete tanimlama (ration builder) kapsam disidir.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class FeedItem(TimestampMixin, Base):
    __tablename__ = "feed_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    feed_type_id: Mapped[int] = mapped_column(ForeignKey("feed_types.id"), nullable=False)
    default_unit_id: Mapped[int] = mapped_column(ForeignKey("feed_units.id"), nullable=False)

    feed_type = relationship("FeedType")
    default_unit = relationship("FeedUnit")


class FeedDistribution(TimestampMixin, Base):
    __tablename__ = "feed_distributions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pen_id: Mapped[int] = mapped_column(ForeignKey("pens.id"), nullable=False, index=True)
    feed_item_id: Mapped[int] = mapped_column(ForeignKey("feed_items.id"), nullable=False)
    distribution_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("feed_units.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    pen = relationship("Pen")
    feed_item = relationship("FeedItem")
    unit = relationship("FeedUnit")
