"""Doviz kuru onbellek tablosu.

TCMB'nin herkese acik gunluk kur XML servisinden cekilen USD/TRY satis
kurlarini tarih bazinda onbelleğe alir. Bu, hicbir maliyet tablosuna
(Animal/FeedDistribution/HealthEvent) eklenen bir "fact" DEGILDIR - dis
kaynakli referans veridir; raporlar USD karsiligini islem tarihi + bu
tablo uzerinden turetir (bkz. service.get_usd_try_rate, Anayasa m.4/m.5).
Bir tarihin kuru bir kez yazildiktan sonra degismez (tarihsel kur sabittir).
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    rate_date: Mapped[date] = mapped_column(Date, primary_key=True)
    usd_try_selling: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
