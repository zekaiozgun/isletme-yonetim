"""Evaluation: hayvan değerlendirme (sürüden çıkarma / damızlık önerisi) günlüğü.

Sürüden çıkarma ve damızlık önerisi TEK bir sürü değerlendirmesi
felsefesinin iki kutbudur - ayni tabloda (animal_evaluations) tutulur;
hangi kutba ait oldugu reason_id uzerinden (EvaluationReason.direction_id)
belirlenir. animal_evaluations'ta AYRICA bir direction alani YOKTUR
(Anayasa m.4/m.5: reason'dan turetilebilir bir deger ikinci kez saklanmaz).

Append-only bir GOZLEM gunlugudur - Sale/Death'in aksine (Anayasa m.8)
kapatma/statu YOKTUR: ayni hayvan icin zaman icinde birden fazla kayit
birikebilir, biri digerini "kapatmaz" - kullanici gecmisi yorumlar
(degerlendirme genellikle gozlemlenen bir soruna iliskindir, "cozuldu"
diye isaretlenecek bir sey degildir).
"""

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class EvaluationReason(TimestampMixin, Base):
    """Değerlendirme nedeni - hangi yöne (EvaluationDirection) ait olduğunu
    kendi üzerinde taşır, bu yüzden LookupMixin (code/name/is_active) değil,
    Medication'a benzer ayrı bir model (bkz. health/models.py)."""

    __tablename__ = "evaluation_reasons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    direction_id: Mapped[int] = mapped_column(ForeignKey("evaluation_directions.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    direction = relationship("EvaluationDirection")


class AnimalEvaluation(TimestampMixin, Base):
    __tablename__ = "animal_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    animal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, index=True
    )
    evaluation_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason_id: Mapped[int] = mapped_column(ForeignKey("evaluation_reasons.id"), nullable=False)
    # Sadece "Suruden Cikarma" yonundeki nedenler icin anlamlidir (Damizlik
    # Onerisi'nde triyaj ihtiyaci yoktur) - opsiyonel, formda her iki yonde
    # de gosterilir, raporlar sadece ilgili yonde doldurur.
    priority_id: Mapped[int | None] = mapped_column(ForeignKey("evaluation_priorities.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    animal = relationship("Animal")
    reason = relationship("EvaluationReason")
    priority = relationship("EvaluationPriority")
