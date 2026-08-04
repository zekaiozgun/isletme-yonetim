import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.evaluation import service
from app.modules.evaluation.lookups import EvaluationDirection, EvaluationPriority
from app.modules.evaluation.schemas import (
    AnimalEvaluationCreate,
    AnimalEvaluationRead,
    EvaluationReasonCreate,
    EvaluationReasonRead,
)

router = APIRouter(prefix="/evaluations", tags=["evaluation"])


@router.post("/reasons", response_model=EvaluationReasonRead, status_code=201)
def create_evaluation_reason(payload: EvaluationReasonCreate, db: Session = Depends(get_db)) -> EvaluationReasonRead:
    return service.create_evaluation_reason(db, payload)


@router.get("/reasons", response_model=list[EvaluationReasonRead])
def list_evaluation_reasons(
    direction_id: int | None = None, db: Session = Depends(get_db)
) -> list[EvaluationReasonRead]:
    return service.list_evaluation_reasons(db, direction_id)


@router.get("/reasons/{reason_id}", response_model=EvaluationReasonRead)
def get_evaluation_reason(reason_id: int, db: Session = Depends(get_db)) -> EvaluationReasonRead:
    try:
        return service.get_evaluation_reason(db, reason_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/reasons/{reason_id}", response_model=EvaluationReasonRead)
def update_evaluation_reason(
    reason_id: int, payload: EvaluationReasonCreate, db: Session = Depends(get_db)
) -> EvaluationReasonRead:
    try:
        return service.update_evaluation_reason(db, reason_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/reasons/{reason_id}", status_code=204)
def delete_evaluation_reason(reason_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_evaluation_reason(db, reason_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


lookup_routers = [
    build_lookup_router(EvaluationDirection, "/directions", "evaluation-lookups", "değerlendirme yönü"),
    build_lookup_router(EvaluationPriority, "/priorities", "evaluation-lookups", "öncelik"),
]
for lookup_router in lookup_routers:
    router.include_router(lookup_router)


@router.post("", response_model=AnimalEvaluationRead, status_code=201)
def create_animal_evaluation(payload: AnimalEvaluationCreate, db: Session = Depends(get_db)) -> AnimalEvaluationRead:
    return service.create_animal_evaluation(db, payload)


@router.get("", response_model=list[AnimalEvaluationRead])
def list_all_animal_evaluations(
    animal_id: uuid.UUID | None = None, db: Session = Depends(get_db)
) -> list[AnimalEvaluationRead]:
    return service.list_animal_evaluations(db, animal_id=animal_id)


@router.get("/animals/{animal_id}", response_model=list[AnimalEvaluationRead])
def list_animal_evaluations(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> list[AnimalEvaluationRead]:
    return service.list_animal_evaluations(db, animal_id)


# NOT: /{evaluation_id} (tek segment, wildcard), yukaridaki /reasons,
# /directions, /priorities, /animals route'larindan SONRA tanimlanmalidir.
@router.get("/{evaluation_id}", response_model=AnimalEvaluationRead)
def get_animal_evaluation(evaluation_id: int, db: Session = Depends(get_db)) -> AnimalEvaluationRead:
    try:
        return service.get_animal_evaluation(db, evaluation_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{evaluation_id}", response_model=AnimalEvaluationRead)
def update_animal_evaluation(
    evaluation_id: int, payload: AnimalEvaluationCreate, db: Session = Depends(get_db)
) -> AnimalEvaluationRead:
    try:
        return service.update_animal_evaluation(db, evaluation_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{evaluation_id}", status_code=204)
def delete_animal_evaluation(evaluation_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_animal_evaluation(db, evaluation_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
