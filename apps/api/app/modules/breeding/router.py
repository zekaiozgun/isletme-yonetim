import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.breeding import service
from app.modules.breeding.lookups import PregnancyCheckMethod, PregnancyResult, ServiceMethod
from app.modules.breeding.schemas import (
    BreedingEventCreate,
    BreedingEventRead,
    PregnancyCheckCreate,
    PregnancyCheckRead,
)

router = APIRouter(prefix="/breeding-events", tags=["breeding"])


@router.post("", response_model=BreedingEventRead, status_code=201)
def create_breeding_event(payload: BreedingEventCreate, db: Session = Depends(get_db)) -> BreedingEventRead:
    return service.create_breeding_event(db, payload)


@router.get("", response_model=list[BreedingEventRead])
def list_breeding_events(
    dam_id: uuid.UUID | None = None,
    pending_check: bool | None = None,
    db: Session = Depends(get_db),
) -> list[BreedingEventRead]:
    return service.list_breeding_events(db, dam_id=dam_id, pending_check=pending_check)


@router.get("/expected-calving-date")
def get_expected_calving_date(service_date: date) -> dict[str, date]:
    return {"expected_calving_date": service.calculate_expected_calving_date(service_date)}


@router.post("/pregnancy-checks", response_model=PregnancyCheckRead, status_code=201)
def create_pregnancy_check(payload: PregnancyCheckCreate, db: Session = Depends(get_db)) -> PregnancyCheckRead:
    return service.create_pregnancy_check(db, payload)


@router.get("/pregnancy-checks", response_model=list[PregnancyCheckRead])
def list_all_pregnancy_checks(
    breeding_event_id: int | None = None, db: Session = Depends(get_db)
) -> list[PregnancyCheckRead]:
    return service.list_pregnancy_checks(db, breeding_event_id=breeding_event_id)


@router.get("/{breeding_event_id}/pregnancy-checks", response_model=list[PregnancyCheckRead])
def list_pregnancy_checks(breeding_event_id: int, db: Session = Depends(get_db)) -> list[PregnancyCheckRead]:
    return service.list_pregnancy_checks(db, breeding_event_id)


@router.get("/pregnancy-checks/{check_id}", response_model=PregnancyCheckRead)
def get_pregnancy_check(check_id: int, db: Session = Depends(get_db)) -> PregnancyCheckRead:
    try:
        return service.get_pregnancy_check(db, check_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/pregnancy-checks/{check_id}", response_model=PregnancyCheckRead)
def update_pregnancy_check(check_id: int, payload: PregnancyCheckCreate, db: Session = Depends(get_db)) -> PregnancyCheckRead:
    try:
        return service.update_pregnancy_check(db, check_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/pregnancy-checks/{check_id}", status_code=204)
def delete_pregnancy_check(check_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_pregnancy_check(db, check_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


lookup_routers = [
    build_lookup_router(ServiceMethod, "/service-methods", "breeding-lookups", "aşım yöntemi"),
    build_lookup_router(PregnancyCheckMethod, "/pregnancy-check-methods", "breeding-lookups", "gebelik kontrol yöntemi"),
    build_lookup_router(PregnancyResult, "/pregnancy-results", "breeding-lookups", "gebelik sonucu"),
]
for lookup_router in lookup_routers:
    router.include_router(lookup_router)


# NOT: /{breeding_event_id} (tek segment, wildcard), yukaridaki tum literal
# tek-segment route'lardan (expected-calving-date, pregnancy-checks,
# service-methods, pregnancy-check-methods, pregnancy-results) SONRA
# tanimlanmalidir.
@router.get("/{breeding_event_id}", response_model=BreedingEventRead)
def get_breeding_event(breeding_event_id: int, db: Session = Depends(get_db)) -> BreedingEventRead:
    try:
        return service.get_breeding_event(db, breeding_event_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{breeding_event_id}", response_model=BreedingEventRead)
def update_breeding_event(breeding_event_id: int, payload: BreedingEventCreate, db: Session = Depends(get_db)) -> BreedingEventRead:
    try:
        return service.update_breeding_event(db, breeding_event_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{breeding_event_id}", status_code=204)
def delete_breeding_event(breeding_event_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_breeding_event(db, breeding_event_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
