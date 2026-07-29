from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.feed import service
from app.modules.feed.lookups import FeedType, FeedUnit
from app.modules.feed.schemas import (
    FeedItemCreate,
    FeedItemRead,
    FeedPurchaseCreate,
    FeedPurchaseRead,
    PenRationCreate,
    PenRationRead,
)

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


@router.post("/purchases", response_model=FeedPurchaseRead, status_code=201)
def create_feed_purchase(payload: FeedPurchaseCreate, db: Session = Depends(get_db)) -> FeedPurchaseRead:
    return service.create_feed_purchase(db, payload)


@router.get("/purchases", response_model=list[FeedPurchaseRead])
def list_feed_purchases(feed_item_id: int | None = None, db: Session = Depends(get_db)) -> list[FeedPurchaseRead]:
    return service.list_feed_purchases(db, feed_item_id=feed_item_id)


@router.get("/purchases/{purchase_id}", response_model=FeedPurchaseRead)
def get_feed_purchase(purchase_id: int, db: Session = Depends(get_db)) -> FeedPurchaseRead:
    try:
        return service.get_feed_purchase(db, purchase_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/purchases/{purchase_id}", response_model=FeedPurchaseRead)
def update_feed_purchase(
    purchase_id: int, payload: FeedPurchaseCreate, db: Session = Depends(get_db)
) -> FeedPurchaseRead:
    try:
        return service.update_feed_purchase(db, purchase_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/purchases/{purchase_id}", status_code=204)
def delete_feed_purchase(purchase_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_feed_purchase(db, purchase_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/rations", response_model=PenRationRead, status_code=201)
def create_pen_ration(payload: PenRationCreate, db: Session = Depends(get_db)) -> PenRationRead:
    try:
        return service.create_pen_ration(db, payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/rations", response_model=list[PenRationRead])
def list_pen_rations(pen_id: int | None = None, db: Session = Depends(get_db)) -> list[PenRationRead]:
    return service.list_pen_rations(db, pen_id=pen_id)


@router.get("/rations/{ration_id}", response_model=PenRationRead)
def get_pen_ration(ration_id: int, db: Session = Depends(get_db)) -> PenRationRead:
    try:
        return service.get_pen_ration(db, ration_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/rations/{ration_id}", response_model=PenRationRead)
def update_pen_ration(ration_id: int, payload: PenRationCreate, db: Session = Depends(get_db)) -> PenRationRead:
    try:
        return service.update_pen_ration(db, ration_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/rations/{ration_id}", status_code=204)
def delete_pen_ration(ration_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_pen_ration(db, ration_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


lookup_routers = [
    build_lookup_router(FeedType, "/types", "feed-lookups", "yem tipi"),
    build_lookup_router(FeedUnit, "/units", "feed-lookups", "yem birimi"),
]
for lookup_router in lookup_routers:
    router.include_router(lookup_router)
