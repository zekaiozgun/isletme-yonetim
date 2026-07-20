import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import DomainError, NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.pen import service
from app.modules.pen.lookups import PenAssignmentReason, PenType
from app.modules.pen.schemas import PenAssignmentCreate, PenAssignmentRead, PenCreate, PenRead

router = APIRouter(prefix="/pens", tags=["pens"])


@router.post("", response_model=PenRead, status_code=201)
def create_pen(payload: PenCreate, db: Session = Depends(get_db)) -> PenRead:
    return service.create_pen(db, payload)


@router.get("", response_model=list[PenRead])
def list_pens(db: Session = Depends(get_db)) -> list[PenRead]:
    return service.list_pens(db)


@router.get("/{pen_id}/assignments", response_model=list[PenAssignmentRead])
def list_pen_assignments(pen_id: int, current_only: bool = False, db: Session = Depends(get_db)) -> list[PenAssignmentRead]:
    return service.list_assignments_for_pen(db, pen_id, current_only=current_only)


@router.post("/assignments", response_model=PenAssignmentRead, status_code=201)
def assign_animal_to_pen(payload: PenAssignmentCreate, db: Session = Depends(get_db)) -> PenAssignmentRead:
    try:
        return service.assign_animal_to_pen(db, payload)
    except DomainError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/assignments", response_model=list[PenAssignmentRead])
def list_all_pen_assignments(
    animal_id: uuid.UUID | None = None, pen_id: int | None = None, db: Session = Depends(get_db)
) -> list[PenAssignmentRead]:
    return service.list_all_assignments(db, animal_id=animal_id, pen_id=pen_id)


@router.get("/animals/{animal_id}/assignments", response_model=list[PenAssignmentRead])
def list_animal_assignments(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> list[PenAssignmentRead]:
    return service.list_assignments_for_animal(db, animal_id)


@router.get("/assignments/{assignment_id}", response_model=PenAssignmentRead)
def get_pen_assignment(assignment_id: int, db: Session = Depends(get_db)) -> PenAssignmentRead:
    try:
        return service.get_assignment(db, assignment_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/assignments/{assignment_id}", response_model=PenAssignmentRead)
def update_pen_assignment(
    assignment_id: int, payload: PenAssignmentCreate, db: Session = Depends(get_db)
) -> PenAssignmentRead:
    try:
        return service.update_assignment(db, assignment_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/assignments/{assignment_id}", status_code=204)
def delete_pen_assignment(assignment_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_assignment(db, assignment_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


lookup_routers = [
    build_lookup_router(PenType, "/pen-types", "pen-lookups", "padok tipi"),
    build_lookup_router(PenAssignmentReason, "/pen-assignment-reasons", "pen-lookups", "padok değişim nedeni"),
]
for lookup_router in lookup_routers:
    router.include_router(lookup_router)


# NOT: /{pen_id} (tek segment, wildcard), yukaridaki tum literal tek-segment
# route'lardan (assignments, pen-types, pen-assignment-reasons) SONRA
# tanimlanmalidir - aksi halde onlari golgeler (bkz. Anayasa/route sirasi notu).
@router.get("/{pen_id}", response_model=PenRead)
def get_pen(pen_id: int, db: Session = Depends(get_db)) -> PenRead:
    try:
        return service.get_pen(db, pen_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{pen_id}", response_model=PenRead)
def update_pen(pen_id: int, payload: PenCreate, db: Session = Depends(get_db)) -> PenRead:
    try:
        return service.update_pen(db, pen_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{pen_id}", status_code=204)
def delete_pen(pen_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_pen(db, pen_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
