from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.valuation.models import GrowthValuationCheckpoint
from app.modules.valuation.schemas import GrowthValuationCheckpointCreate

_CONFLICT_MESSAGE = "Bu cinsiyet/yaş kombinasyonu için zaten bir çıpa girilmiş."


def list_checkpoints(db: Session) -> list[GrowthValuationCheckpoint]:
    stmt = select(GrowthValuationCheckpoint).order_by(
        GrowthValuationCheckpoint.gender_id, GrowthValuationCheckpoint.age_months
    )
    return list(db.scalars(stmt).all())


def create_checkpoint(db: Session, data: GrowthValuationCheckpointCreate) -> GrowthValuationCheckpoint:
    checkpoint = GrowthValuationCheckpoint(**data.model_dump())
    db.add(checkpoint)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(_CONFLICT_MESSAGE) from exc
    db.refresh(checkpoint)
    return checkpoint


def _get_or_404(db: Session, checkpoint_id: int) -> GrowthValuationCheckpoint:
    checkpoint = db.get(GrowthValuationCheckpoint, checkpoint_id)
    if checkpoint is None:
        raise NotFoundError(f"Büyüme değerleme çıpası bulunamadı: {checkpoint_id}")
    return checkpoint


def update_checkpoint(
    db: Session, checkpoint_id: int, data: GrowthValuationCheckpointCreate
) -> GrowthValuationCheckpoint:
    checkpoint = _get_or_404(db, checkpoint_id)
    for key, value in data.model_dump().items():
        setattr(checkpoint, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(_CONFLICT_MESSAGE) from exc
    db.refresh(checkpoint)
    return checkpoint


def delete_checkpoint(db: Session, checkpoint_id: int) -> None:
    checkpoint = _get_or_404(db, checkpoint_id)
    db.delete(checkpoint)
    db.commit()
