from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.expense.models import GeneralExpense
from app.modules.expense.schemas import GeneralExpenseCreate


def create_general_expense(db: Session, data: GeneralExpenseCreate) -> GeneralExpense:
    expense = GeneralExpense(**data.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_general_expense(db: Session, expense_id: int) -> GeneralExpense:
    expense = db.get(GeneralExpense, expense_id)
    if expense is None:
        raise NotFoundError(f"GeneralExpense bulunamadi: {expense_id}")
    return expense


def update_general_expense(db: Session, expense_id: int, data: GeneralExpenseCreate) -> GeneralExpense:
    expense = get_general_expense(db, expense_id)
    for key, value in data.model_dump().items():
        setattr(expense, key, value)
    db.commit()
    db.refresh(expense)
    return expense


def delete_general_expense(db: Session, expense_id: int) -> None:
    expense = get_general_expense(db, expense_id)
    db.delete(expense)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu gider kaydı başka kayıtlar tarafından kullanıldığı için silinemez.") from exc


def list_general_expenses(db: Session) -> list[GeneralExpense]:
    return list(db.scalars(select(GeneralExpense).order_by(GeneralExpense.expense_date.desc())).all())
