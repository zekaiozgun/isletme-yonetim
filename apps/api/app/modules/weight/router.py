import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.weight import service
from app.modules.weight.lookups import WeighingMethod
from app.modules.weight.schemas import WeightRecordCreate, WeightRecordRead

router = APIRouter(prefix="/weight-records", tags=["weight"])


@router.post("", response_model=WeightRecordRead, status_code=201)
def create_weight_record(payload: WeightRecordCreate, db: Session = Depends(get_db)) -> WeightRecordRead:
    return service.create_weight_record(db, payload)


@router.get("", response_model=list[WeightRecordRead])
def list_all_weight_records(animal_id: uuid.UUID | None = None, db: Session = Depends(get_db)) -> list[WeightRecordRead]:
    return service.list_weight_records(db, animal_id=animal_id)


@router.get("/animals/{animal_id}", response_model=list[WeightRecordRead])
def list_weight_records(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> list[WeightRecordRead]:
    return service.list_weight_records(db, animal_id)


@router.get("/animals/{animal_id}/average-daily-gain")
def get_average_daily_gain(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> dict[str, Decimal | None]:
    return {"adg_kg_per_day": service.calculate_average_daily_gain(db, animal_id)}


router.include_router(build_lookup_router(WeighingMethod, "/weighing-methods", "weight-lookups", "tartı yöntemi"))


# NOT: /{record_id} yukaridaki /weighing-methods (literal, tek segment)
# route'undan SONRA tanimlanmalidir - route sirasi notu icin animal/router.py'ye bakin.
@router.get("/{record_id}", response_model=WeightRecordRead)
def get_weight_record(record_id: int, db: Session = Depends(get_db)) -> WeightRecordRead:
    try:
        return service.get_weight_record(db, record_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{record_id}", response_model=WeightRecordRead)
def update_weight_record(record_id: int, payload: WeightRecordCreate, db: Session = Depends(get_db)) -> WeightRecordRead:
    try:
        return service.update_weight_record(db, record_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{record_id}", status_code=204)
def delete_weight_record(record_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_weight_record(db, record_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
