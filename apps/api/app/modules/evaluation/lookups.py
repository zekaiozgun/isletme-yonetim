"""Master Data (lookup) tables for the Evaluation bounded context."""

from app.core.database import Base
from app.core.orm import LookupMixin


class EvaluationDirection(LookupMixin, Base):
    """Değerlendirme Yönü (Sürüden Çıkarma / Damızlık Önerisi) - sürü
    değerlendirmesinin iki kutbu."""

    __tablename__ = "evaluation_directions"


class EvaluationPriority(LookupMixin, Base):
    """Öncelik (Düşük/Orta/Yüksek) - sadece Sürüden Çıkarma yönünde
    triyaj icin anlamlidir, Damizlik Onerisi'nde kullanilmaz."""

    __tablename__ = "evaluation_priorities"
