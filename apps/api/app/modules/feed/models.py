"""Feed: yem urunu master verisi, alim (stok girisi) ve padok rasyonlari.

V2: gunluk "dagitim" kaydi YERINE, bir padoga uygulanan rasyon (hangi
yem kaleminden hayvan basina gunde ne kadar) DONEM olarak girilir - yeni
bir rasyon girildiginde onceki donem otomatik kapanir (bkz. service.py
create_pen_ration). Gercek tuketim/maliyet hicbir yerde SAKLANMAZ; rasyon
donemi ile padogun fiilen dolu oldugu gunlerin kesisiminden (pen_assignments)
istek aninda turetilir (Anayasa m.4/m.5, bkz. reports/service.py).

Yem stogu da ayni sekilde turetilir: toplam alim - toplam tuketim.
Agirlikli ortalama birim maliyet (TL/kg), alim kayitlarindan turetilir ve
hem rasyon maliyetinde hem stok degerinde kullanilir - birim fiyat hicbir
yerde elle girilmez (Anayasa m.4).
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


class FeedPurchase(TimestampMixin, Base):
    """Yem stogu GIRIS (alim) kaydi - stok ve agirlikli ortalama maliyet
    buradan turetilir (bkz. reports/service.py _feed_avg_cost_per_kg)."""

    __tablename__ = "feed_purchases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    feed_item_id: Mapped[int] = mapped_column(ForeignKey("feed_items.id"), nullable=False, index=True)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("feed_units.id"), nullable=False)
    # Fatura/fis tutari fact olarak girilir (Anayasa m.4) - birim fiyat
    # sistem tarafindan HESAPLANMAZ, agirlikli ortalama bu facttan turetilir.
    total_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    feed_item = relationship("FeedItem")
    unit = relationship("FeedUnit")


class PenRation(TimestampMixin, Base):
    """Bir padoga uygulanan rasyon DONEMI. Ayni padoga yeni bir rasyon
    girildiginde bu kaydin end_date'i otomatik doldurulur (bkz.
    service.create_pen_ration) - end_date NULL ise hala gecerlidir."""

    __tablename__ = "pen_rations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pen_id: Mapped[int] = mapped_column(ForeignKey("pens.id"), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    pen = relationship("Pen")
    items: Mapped[list["RationItem"]] = relationship(
        "RationItem", back_populates="ration", cascade="all, delete-orphan", order_by="RationItem.id"
    )


class RationItem(TimestampMixin, Base):
    """Bir rasyon doneminin icerigi: hangi yem kaleminden HAYVAN BASINA
    gunde ne kadar verilir. Padoktaki toplam miktar, o gunku fiili hayvan
    sayisiyla ÇARPILARAK istek aninda turetilir - elle toplam girilmez,
    hayvan sayisi degistikce (satis/olum/giris) otomatik dogru kalir.

    scope_id (bkz. RationItemScope): bu kalem padoktaki HANGI yas grubuna
    uygulanir - varsayilan TUMU (mevcut/eski davranis). Anne-yavru
    padoklarinda buzagilarin yetiskinlerle homojen sayilmamasi
    (yetiskin rasyonuna dahil edilmemesi) veya ayri bir buzagi buyutme
    yeminin sadece buzagi sayisina bolunmesi icin kullanilir - yasa gore
    filtreleme istek aninda turetilir (Anayasa m.4/m.5), hicbir hayvan
    burada isimlendirilmez."""

    __tablename__ = "ration_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ration_id: Mapped[int] = mapped_column(ForeignKey("pen_rations.id"), nullable=False, index=True)
    feed_item_id: Mapped[int] = mapped_column(ForeignKey("feed_items.id"), nullable=False)
    daily_quantity_per_animal: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("feed_units.id"), nullable=False)
    scope_id: Mapped[int] = mapped_column(ForeignKey("ration_item_scopes.id"), nullable=False)

    ration = relationship("PenRation", back_populates="items")
    feed_item = relationship("FeedItem")
    unit = relationship("FeedUnit")
    scope = relationship("RationItemScope")
