from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.valuation import service
from app.modules.valuation.schemas import GrowthValuationCheckpointCreate, GrowthValuationCheckpointRead

router = APIRouter(prefix="/growth-valuation-checkpoints", tags=["valuation"])


@router.get("", response_model=list[GrowthValuationCheckpointRead])
def list_checkpoints(db: Session = Depends(get_db)) -> list[GrowthValuationCheckpointRead]:
    return service.list_checkpoints(db)


@router.post("", response_model=GrowthValuationCheckpointRead, status_code=201)
def create_checkpoint(
    payload: GrowthValuationCheckpointCreate, db: Session = Depends(get_db)
) -> GrowthValuationCheckpointRead:
    return service.create_checkpoint(db, payload)


@router.put("/{checkpoint_id}", response_model=GrowthValuationCheckpointRead)
def update_checkpoint(
    checkpoint_id: int, payload: GrowthValuationCheckpointCreate, db: Session = Depends(get_db)
) -> GrowthValuationCheckpointRead:
    return service.update_checkpoint(db, checkpoint_id, payload)


@router.delete("/{checkpoint_id}", status_code=204)
def delete_checkpoint(checkpoint_id: int, db: Session = Depends(get_db)) -> None:
    service.delete_checkpoint(db, checkpoint_id)
