"""Büyüme Değerleme Çıpası: Malzeme durumundaki (henüz Demirbaşa geçmemiş)
hayvanların tahmini piyasa değerini hesaplamak için kullanıcının girdiği,
yaşa bağlı gerçek piyasa fiyatları (Anayasa m.4/m.6: sistem bir büyüme
oranı TAHMİN ETMEZ, kullanıcının gözlemlediği piyasa verisini toplar).

12 aylık çıpa cinsiyete göre farklı, gerçek bir piyasa kategorisini
temsil eder: Erkek için "12 Aylık Besilik Erkek Dana Fiyatı", Dişi için
"12 Aylık Tohumlanmış/Gebe Düve Fiyatı" (bkz. reports/service.py
_market_value_estimate_usd).

Zaman-versiyonlu DEĞİLDİR (exchange_rates tablosunun aksine) - GÜNCEL
değeri tutar; bir çıpa güncellendiğinde geçmiş tarihli raporlar da yeni
rakamla yeniden hesaplanır (kasıtlı basitleştirme, kullanıcı onayı ile)."""

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class GrowthValuationCheckpoint(TimestampMixin, Base):
    __tablename__ = "growth_valuation_checkpoints"
    __table_args__ = (
        CheckConstraint("age_months IN (3, 6, 9, 12)", name="ck_growth_checkpoint_age_months"),
        UniqueConstraint("gender_id", "age_months", name="uq_growth_checkpoint_gender_age"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gender_id: Mapped[int] = mapped_column(ForeignKey("genders.id"), nullable=False)
    age_months: Mapped[int] = mapped_column(nullable=False)
    value_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    gender = relationship("Gender")
