"""Büyüme Değerleme Çıpası: Malzeme durumundaki (henüz Demirbaşa geçmemiş)
genç hayvanların VE olgun (Demirbaş) dişilerin tahmini piyasa değerini
hesaplamak için kullanıcının girdiği, gerçek piyasa fiyatları (Anayasa
m.4/m.6: sistem bir büyüme oranı TAHMİN ETMEZ, kullanıcının gözlemlediği
piyasa verisini toplar). Değerler TL olarak girilir - USD karşılığı,
rapor üretilirken işlem tarihindeki TCMB kuruyla türetilir (Anayasa m.4/m.5
- bkz. reports/service.py), tıpkı entry_value/sağlık/yem maliyetleri gibi.

category_code altı sabit kategoriden biridir:
  - AGE_3 / AGE_6 / AGE_9 / AGE_12: genç hayvan büyüme eğrisi noktaları
    (Erkek için "Besilik Erkek Dana", Dişi için "Düve" fiyatı - 12 aylık
    dişi çıpası aynı zamanda düvenin gebe kalıp Demirbaşa geçtiği andaki
    referans değeridir, bkz. reports/service.py).
  - GEBE / BOS: olgun (Demirbaşa geçmiş) bir dişinin GÜNCEL üreme
    durumuna göre piyasa değeri - yalnızca Dişi için anlamlıdır.

Zaman-versiyonlu DEĞİLDİR (exchange_rates tablosunun aksine) - GÜNCEL
değeri tutar; bir çıpa güncellendiğinde geçmiş tarihli raporlar da yeni
rakamla yeniden hesaplanır (kasıtlı basitleştirme, kullanıcı onayı ile)."""

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin

CATEGORY_CODES = ("AGE_3", "AGE_6", "AGE_9", "AGE_12", "GEBE", "BOS")


class GrowthValuationCheckpoint(TimestampMixin, Base):
    __tablename__ = "growth_valuation_checkpoints"
    __table_args__ = (
        CheckConstraint(
            "category_code IN ('AGE_3','AGE_6','AGE_9','AGE_12','GEBE','BOS')",
            name="ck_growth_checkpoint_category",
        ),
        UniqueConstraint("gender_id", "category_code", name="uq_growth_checkpoint_gender_category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gender_id: Mapped[int] = mapped_column(ForeignKey("genders.id"), nullable=False)
    category_code: Mapped[str] = mapped_column(String(16), nullable=False)
    value_try: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    gender = relationship("Gender")
