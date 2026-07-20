from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.modules.genetic_resource import service
from app.modules.genetic_resource.schemas import SemenBatchCreate, SemenBatchRead, SireCreate, SireRead

router = APIRouter(prefix="/genetic-resource", tags=["genetic-resource"])


@router.post("/sires", response_model=SireRead, status_code=201)
def create_sire(payload: SireCreate, db: Session = Depends(get_db)) -> SireRead:
    return service.create_sire(db, payload)


@router.get("/sires", response_model=list[SireRead])
def list_sires(db: Session = Depends(get_db)) -> list[SireRead]:
    return service.list_sires(db)


@router.get("/sires/{sire_id}", response_model=SireRead)
def get_sire(sire_id: int, db: Session = Depends(get_db)) -> SireRead:
    try:
        return service.get_sire(db, sire_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/sires/{sire_id}", response_model=SireRead)
def update_sire(sire_id: int, payload: SireCreate, db: Session = Depends(get_db)) -> SireRead:
    try:
        return service.update_sire(db, sire_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/sires/{sire_id}", status_code=204)
def delete_sire(sire_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_sire(db, sire_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/semen-batches", response_model=SemenBatchRead, status_code=201)
def create_semen_batch(payload: SemenBatchCreate, db: Session = Depends(get_db)) -> SemenBatchRead:
    return service.create_semen_batch(db, payload)


@router.get("/semen-batches", response_model=list[SemenBatchRead])
def list_semen_batches(sire_id: int | None = None, db: Session = Depends(get_db)) -> list[SemenBatchRead]:
    return service.list_semen_batches(db, sire_id=sire_id)


@router.get("/semen-batches/{batch_id}", response_model=SemenBatchRead)
def get_semen_batch(batch_id: int, db: Session = Depends(get_db)) -> SemenBatchRead:
    try:
        return service.get_semen_batch(db, batch_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/semen-batches/{batch_id}", response_model=SemenBatchRead)
def update_semen_batch(batch_id: int, payload: SemenBatchCreate, db: Session = Depends(get_db)) -> SemenBatchRead:
    try:
        return service.update_semen_batch(db, batch_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/semen-batches/{batch_id}", status_code=204)
def delete_semen_batch(batch_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_semen_batch(db, batch_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
