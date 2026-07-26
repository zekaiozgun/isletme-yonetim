from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.valuation import service
from app.modules.valuation.schemas import GrowthValuationCheckpointBulkUpdate, GrowthValuationCheckpointRead

router = APIRouter(prefix="/growth-valuation-checkpoints", tags=["valuation"])


@router.get("", response_model=list[GrowthValuationCheckpointRead])
def list_checkpoints(db: Session = Depends(get_db)) -> list[GrowthValuationCheckpointRead]:
    return service.list_checkpoints(db)


@router.put("", response_model=list[GrowthValuationCheckpointRead])
def replace_checkpoints(
    payload: GrowthValuationCheckpointBulkUpdate, db: Session = Depends(get_db)
) -> list[GrowthValuationCheckpointRead]:
    return service.replace_checkpoints(db, payload.items)
