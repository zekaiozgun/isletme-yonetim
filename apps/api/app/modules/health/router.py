import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.health import service
from app.modules.health.lookups import Disease, DosageUnit, HealthEventType, MedicationType
from app.modules.health.schemas import HealthEventCreate, HealthEventRead, MedicationCreate, MedicationRead

router = APIRouter(prefix="/health-events", tags=["health"])


@router.post("/medications", response_model=MedicationRead, status_code=201)
def create_medication(payload: MedicationCreate, db: Session = Depends(get_db)) -> MedicationRead:
    return service.create_medication(db, payload)


@router.get("/medications", response_model=list[MedicationRead])
def list_medications(db: Session = Depends(get_db)) -> list[MedicationRead]:
    return service.list_medications(db)


@router.get("/medications/{medication_id}", response_model=MedicationRead)
def get_medication(medication_id: int, db: Session = Depends(get_db)) -> MedicationRead:
    try:
        return service.get_medication(db, medication_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/medications/{medication_id}", response_model=MedicationRead)
def update_medication(medication_id: int, payload: MedicationCreate, db: Session = Depends(get_db)) -> MedicationRead:
    try:
        return service.update_medication(db, medication_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/medications/{medication_id}", status_code=204)
def delete_medication(medication_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_medication(db, medication_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=HealthEventRead, status_code=201)
def create_health_event(payload: HealthEventCreate, db: Session = Depends(get_db)) -> HealthEventRead:
    return service.create_health_event(db, payload)


@router.get("", response_model=list[HealthEventRead])
def list_all_health_events(animal_id: uuid.UUID | None = None, db: Session = Depends(get_db)) -> list[HealthEventRead]:
    return service.list_health_events(db, animal_id=animal_id)


@router.get("/animals/{animal_id}", response_model=list[HealthEventRead])
def list_health_events(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> list[HealthEventRead]:
    return service.list_health_events(db, animal_id)


@router.get("/{health_event_id}/withdrawal-end-date")
def get_withdrawal_end_date(health_event_id: int, db: Session = Depends(get_db)) -> dict[str, date | None]:
    return {"withdrawal_end_date": service.calculate_withdrawal_end_date(db, health_event_id)}


lookup_routers = [
    build_lookup_router(HealthEventType, "/event-types", "health-lookups", "sağlık olayı tipi"),
    build_lookup_router(Disease, "/diseases", "health-lookups", "hastalık"),
    build_lookup_router(MedicationType, "/medication-types", "health-lookups", "ilaç tipi"),
    build_lookup_router(DosageUnit, "/dosage-units", "health-lookups", "doz birimi"),
]
for lookup_router in lookup_routers:
    router.include_router(lookup_router)


# NOT: /{health_event_id} (tek segment, wildcard), yukaridaki /medications
# ve 4 lookup route'undan SONRA tanimlanmalidir.
@router.get("/{health_event_id}", response_model=HealthEventRead)
def get_health_event(health_event_id: int, db: Session = Depends(get_db)) -> HealthEventRead:
    try:
        return service.get_health_event(db, health_event_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{health_event_id}", response_model=HealthEventRead)
def update_health_event(health_event_id: int, payload: HealthEventCreate, db: Session = Depends(get_db)) -> HealthEventRead:
    try:
        return service.update_health_event(db, health_event_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{health_event_id}", status_code=204)
def delete_health_event(health_event_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_health_event(db, health_event_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
