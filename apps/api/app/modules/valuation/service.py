from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.valuation.models import GrowthValuationCheckpoint
from app.modules.valuation.schemas import GrowthValuationCheckpointItem


def list_checkpoints(db: Session) -> list[GrowthValuationCheckpoint]:
    stmt = select(GrowthValuationCheckpoint).order_by(
        GrowthValuationCheckpoint.gender_id, GrowthValuationCheckpoint.category_code
    )
    return list(db.scalars(stmt).all())


def replace_checkpoints(db: Session, items: list[GrowthValuationCheckpointItem]) -> list[GrowthValuationCheckpoint]:
    """Tablo formundan gelen TÜM hücreleri (gender_id, category_code) bazında
    işler: değer boşsa (None) var olan çıpayı siler, doluysa oluşturur/
    günceller - gönderilen tablo, o an DB'de ne varsa onu birebir yansıtır."""
    for item in items:
        existing = db.scalar(
            select(GrowthValuationCheckpoint).where(
                GrowthValuationCheckpoint.gender_id == item.gender_id,
                GrowthValuationCheckpoint.category_code == item.category_code,
            )
        )
        if item.value_try is None:
            if existing is not None:
                db.delete(existing)
        elif existing is not None:
            existing.value_try = item.value_try
        else:
            db.add(
                GrowthValuationCheckpoint(
                    gender_id=item.gender_id, category_code=item.category_code, value_try=item.value_try
                )
            )
    db.commit()
    return list_checkpoints(db)
