from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.death import service
from app.modules.death.lookups import DisposalMethod
from app.modules.death.schemas import DeathCreate, DeathRead

router = APIRouter(prefix="/deaths", tags=["death"])


@router.post("", response_model=DeathRead, status_code=201)
def create_death(payload: DeathCreate, db: Session = Depends(get_db)) -> DeathRead:
    return service.create_death(db, payload)


@router.get("", response_model=list[DeathRead])
def list_deaths(db: Session = Depends(get_db)) -> list[DeathRead]:
    return service.list_deaths(db)


router.include_router(build_lookup_router(DisposalMethod, "/disposal-methods", "death-lookups", "imha yöntemi"))


# NOT: /{death_id} (tek segment, wildcard), yukaridaki /disposal-methods
# route'undan SONRA tanimlanmalidir.
@router.get("/{death_id}", response_model=DeathRead)
def get_death(death_id: int, db: Session = Depends(get_db)) -> DeathRead:
    try:
        return service.get_death(db, death_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{death_id}", response_model=DeathRead)
def update_death(death_id: int, payload: DeathCreate, db: Session = Depends(get_db)) -> DeathRead:
    try:
        return service.update_death(db, death_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{death_id}", status_code=204)
def delete_death(death_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_death(db, death_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
