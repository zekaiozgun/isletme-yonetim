"""Evaluation servis katmani.

Sale/Death'in aksine Animal.status'u SENKRONIZE ETMEZ - degerlendirme bir
gozlem/oneri kaydidir, hayvanin surudeki durumunu degistirmez (Anayasa m.8
sadece Sale/Death gibi fiili CIKIS olaylari icin gecerlidir).
"""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.validators import require_date_order
from app.modules.animal.models import Animal
from app.modules.evaluation.models import AnimalEvaluation, EvaluationReason
from app.modules.evaluation.schemas import AnimalEvaluationCreate, EvaluationReasonCreate


def _validate_evaluation_date(db: Session, evaluation: AnimalEvaluation) -> None:
    animal = db.get(Animal, evaluation.animal_id)
    if animal is not None:
        require_date_order(animal.birth_date, "Doğum tarihi", evaluation.evaluation_date, "Değerlendirme tarihi")


def create_evaluation_reason(db: Session, data: EvaluationReasonCreate) -> EvaluationReason:
    reason = EvaluationReason(**data.model_dump())
    db.add(reason)
    db.commit()
    db.refresh(reason)
    return reason


def get_evaluation_reason(db: Session, reason_id: int) -> EvaluationReason:
    reason = db.get(EvaluationReason, reason_id)
    if reason is None:
        raise NotFoundError(f"EvaluationReason bulunamadi: {reason_id}")
    return reason


def update_evaluation_reason(db: Session, reason_id: int, data: EvaluationReasonCreate) -> EvaluationReason:
    reason = get_evaluation_reason(db, reason_id)
    for key, value in data.model_dump().items():
        setattr(reason, key, value)
    db.commit()
    db.refresh(reason)
    return reason


def delete_evaluation_reason(db: Session, reason_id: int) -> None:
    reason = get_evaluation_reason(db, reason_id)
    db.delete(reason)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu değerlendirme nedeni başka kayıtlar tarafından kullanıldığı için silinemez.") from exc


def list_evaluation_reasons(db: Session, direction_id: int | None = None) -> list[EvaluationReason]:
    stmt = select(EvaluationReason)
    if direction_id is not None:
        stmt = stmt.where(EvaluationReason.direction_id == direction_id)
    return list(db.scalars(stmt.order_by(EvaluationReason.name)).all())


def create_animal_evaluation(db: Session, data: AnimalEvaluationCreate) -> AnimalEvaluation:
    evaluation = AnimalEvaluation(**data.model_dump())
    _validate_evaluation_date(db, evaluation)
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation


def get_animal_evaluation(db: Session, evaluation_id: int) -> AnimalEvaluation:
    evaluation = db.get(AnimalEvaluation, evaluation_id)
    if evaluation is None:
        raise NotFoundError(f"AnimalEvaluation bulunamadi: {evaluation_id}")
    return evaluation


def update_animal_evaluation(db: Session, evaluation_id: int, data: AnimalEvaluationCreate) -> AnimalEvaluation:
    evaluation = get_animal_evaluation(db, evaluation_id)
    for key, value in data.model_dump().items():
        setattr(evaluation, key, value)
    _validate_evaluation_date(db, evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation


def delete_animal_evaluation(db: Session, evaluation_id: int) -> None:
    evaluation = get_animal_evaluation(db, evaluation_id)
    db.delete(evaluation)
    db.commit()


def list_animal_evaluations(db: Session, animal_id: uuid.UUID | None = None) -> list[AnimalEvaluation]:
    stmt = select(AnimalEvaluation)
    if animal_id is not None:
        stmt = stmt.where(AnimalEvaluation.animal_id == animal_id)
    return list(db.scalars(stmt.order_by(AnimalEvaluation.evaluation_date)).all())
