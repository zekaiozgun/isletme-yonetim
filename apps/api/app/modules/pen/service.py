"""Pen servis katmani.

assign_animal_to_pen, 'guncel konum = removed_date IS NULL' degismezini
(invariant) korur: yeni bir atama acilmadan once, hayvanin varsa acik
olan onceki atamasi kapatilir (Anayasa m.8 - event gecmisi silinmez,
sadece kapatilir).
"""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, DomainError, NotFoundError
from app.modules.pen.models import Pen, PenAssignment
from app.modules.pen.schemas import PenAssignmentCreate, PenCreate


def create_pen(db: Session, data: PenCreate) -> Pen:
    pen = Pen(**data.model_dump())
    db.add(pen)
    db.commit()
    db.refresh(pen)
    return pen


def get_pen(db: Session, pen_id: int) -> Pen:
    pen = db.get(Pen, pen_id)
    if pen is None:
        raise NotFoundError(f"Pen bulunamadi: {pen_id}")
    return pen


def update_pen(db: Session, pen_id: int, data: PenCreate) -> Pen:
    pen = get_pen(db, pen_id)
    for key, value in data.model_dump().items():
        setattr(pen, key, value)
    db.commit()
    db.refresh(pen)
    return pen


def delete_pen(db: Session, pen_id: int) -> None:
    pen = get_pen(db, pen_id)
    db.delete(pen)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu padok başka kayıtlar tarafından kullanıldığı için silinemez.") from exc


def list_pens(db: Session) -> list[Pen]:
    return list(db.scalars(select(Pen).order_by(Pen.code)).all())


def get_current_assignment(db: Session, animal_id: uuid.UUID) -> PenAssignment | None:
    stmt = select(PenAssignment).where(
        PenAssignment.animal_id == animal_id, PenAssignment.removed_date.is_(None)
    )
    return db.scalars(stmt).first()


def assign_animal_to_pen(db: Session, data: PenAssignmentCreate) -> PenAssignment:
    open_assignment = get_current_assignment(db, data.animal_id)
    if open_assignment is not None:
        if open_assignment.pen_id == data.pen_id:
            raise DomainError("Hayvan zaten bu padokta")
        open_assignment.removed_date = data.assigned_date

    assignment = PenAssignment(**data.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def get_assignment(db: Session, assignment_id: int) -> PenAssignment:
    assignment = db.get(PenAssignment, assignment_id)
    if assignment is None:
        raise NotFoundError(f"PenAssignment bulunamadi: {assignment_id}")
    return assignment


def update_assignment(db: Session, assignment_id: int, data: PenAssignmentCreate) -> PenAssignment:
    assignment = get_assignment(db, assignment_id)
    for key, value in data.model_dump().items():
        setattr(assignment, key, value)
    db.commit()
    db.refresh(assignment)
    return assignment


def delete_assignment(db: Session, assignment_id: int) -> None:
    assignment = get_assignment(db, assignment_id)
    db.delete(assignment)
    db.commit()


def list_all_assignments(
    db: Session, animal_id: uuid.UUID | None = None, pen_id: int | None = None
) -> list[PenAssignment]:
    stmt = select(PenAssignment)
    if animal_id is not None:
        stmt = stmt.where(PenAssignment.animal_id == animal_id)
    if pen_id is not None:
        stmt = stmt.where(PenAssignment.pen_id == pen_id)
    return list(db.scalars(stmt.order_by(PenAssignment.assigned_date)).all())


def list_assignments_for_animal(db: Session, animal_id: uuid.UUID) -> list[PenAssignment]:
    stmt = select(PenAssignment).where(PenAssignment.animal_id == animal_id).order_by(PenAssignment.assigned_date)
    return list(db.scalars(stmt).all())


def list_assignments_for_pen(db: Session, pen_id: int, current_only: bool = False) -> list[PenAssignment]:
    stmt = select(PenAssignment).where(PenAssignment.pen_id == pen_id)
    if current_only:
        stmt = stmt.where(PenAssignment.removed_date.is_(None))
    return list(db.scalars(stmt.order_by(PenAssignment.assigned_date)).all())
