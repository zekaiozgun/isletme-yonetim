from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.expense import service
from app.modules.expense.lookups import ExpenseCategory
from app.modules.expense.schemas import GeneralExpenseCreate, GeneralExpenseRead

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=GeneralExpenseRead, status_code=201)
def create_general_expense(payload: GeneralExpenseCreate, db: Session = Depends(get_db)) -> GeneralExpenseRead:
    return service.create_general_expense(db, payload)


@router.get("", response_model=list[GeneralExpenseRead])
def list_general_expenses(db: Session = Depends(get_db)) -> list[GeneralExpenseRead]:
    return service.list_general_expenses(db)


@router.get("/{expense_id}", response_model=GeneralExpenseRead)
def get_general_expense(expense_id: int, db: Session = Depends(get_db)) -> GeneralExpenseRead:
    try:
        return service.get_general_expense(db, expense_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{expense_id}", response_model=GeneralExpenseRead)
def update_general_expense(
    expense_id: int, payload: GeneralExpenseCreate, db: Session = Depends(get_db)
) -> GeneralExpenseRead:
    try:
        return service.update_general_expense(db, expense_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{expense_id}", status_code=204)
def delete_general_expense(expense_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_general_expense(db, expense_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


router.include_router(build_lookup_router(ExpenseCategory, "/categories", "expense-lookups", "gider kategorisi"))
