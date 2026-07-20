from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.feed import service
from app.modules.feed.lookups import FeedType, FeedUnit
from app.modules.feed.schemas import FeedDistributionCreate, FeedDistributionRead, FeedItemCreate, FeedItemRead

router = APIRouter(prefix="/feed", tags=["feed"])


@router.post("/items", response_model=FeedItemRead, status_code=201)
def create_feed_item(payload: FeedItemCreate, db: Session = Depends(get_db)) -> FeedItemRead:
    return service.create_feed_item(db, payload)


@router.get("/items", response_model=list[FeedItemRead])
def list_feed_items(db: Session = Depends(get_db)) -> list[FeedItemRead]:
    return service.list_feed_items(db)


@router.get("/items/{item_id}", response_model=FeedItemRead)
def get_feed_item(item_id: int, db: Session = Depends(get_db)) -> FeedItemRead:
    try:
        return service.get_feed_item(db, item_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/items/{item_id}", response_model=FeedItemRead)
def update_feed_item(item_id: int, payload: FeedItemCreate, db: Session = Depends(get_db)) -> FeedItemRead:
    try:
        return service.update_feed_item(db, item_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/items/{item_id}", status_code=204)
def delete_feed_item(item_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_feed_item(db, item_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/distributions", response_model=FeedDistributionRead, status_code=201)
def create_feed_distribution(payload: FeedDistributionCreate, db: Session = Depends(get_db)) -> FeedDistributionRead:
    return service.create_feed_distribution(db, payload)


@router.get("/distributions", response_model=list[FeedDistributionRead])
def list_all_feed_distributions(pen_id: int | None = None, db: Session = Depends(get_db)) -> list[FeedDistributionRead]:
    return service.list_feed_distributions(db, pen_id=pen_id)


@router.get("/distributions/{distribution_id}", response_model=FeedDistributionRead)
def get_feed_distribution(distribution_id: int, db: Session = Depends(get_db)) -> FeedDistributionRead:
    try:
        return service.get_feed_distribution(db, distribution_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/distributions/{distribution_id}", response_model=FeedDistributionRead)
def update_feed_distribution(
    distribution_id: int, payload: FeedDistributionCreate, db: Session = Depends(get_db)
) -> FeedDistributionRead:
    try:
        return service.update_feed_distribution(db, distribution_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/distributions/{distribution_id}", status_code=204)
def delete_feed_distribution(distribution_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_feed_distribution(db, distribution_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/pens/{pen_id}/distributions", response_model=list[FeedDistributionRead])
def list_feed_distributions(pen_id: int, db: Session = Depends(get_db)) -> list[FeedDistributionRead]:
    return service.list_feed_distributions(db, pen_id)


lookup_routers = [
    build_lookup_router(FeedType, "/types", "feed-lookups", "yem tipi"),
    build_lookup_router(FeedUnit, "/units", "feed-lookups", "yem birimi"),
]
for lookup_router in lookup_routers:
    router.include_router(lookup_router)
