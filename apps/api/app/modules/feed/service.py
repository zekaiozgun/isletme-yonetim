from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.feed.models import FeedItem, FeedPurchase, PenRation, RationItem
from app.modules.feed.schemas import FeedItemCreate, FeedPurchaseCreate, PenRationCreate


def create_feed_item(db: Session, data: FeedItemCreate) -> FeedItem:
    item = FeedItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_feed_item(db: Session, item_id: int) -> FeedItem:
    item = db.get(FeedItem, item_id)
    if item is None:
        raise NotFoundError(f"FeedItem bulunamadi: {item_id}")
    return item


def update_feed_item(db: Session, item_id: int, data: FeedItemCreate) -> FeedItem:
    item = get_feed_item(db, item_id)
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_feed_item(db: Session, item_id: int) -> None:
    item = get_feed_item(db, item_id)
    db.delete(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu yem ürünü başka kayıtlar tarafından kullanıldığı için silinemez.") from exc


def list_feed_items(db: Session) -> list[FeedItem]:
    return list(db.scalars(select(FeedItem).order_by(FeedItem.name)).all())


def create_feed_purchase(db: Session, data: FeedPurchaseCreate) -> FeedPurchase:
    purchase = FeedPurchase(**data.model_dump())
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


def get_feed_purchase(db: Session, purchase_id: int) -> FeedPurchase:
    purchase = db.get(FeedPurchase, purchase_id)
    if purchase is None:
        raise NotFoundError(f"FeedPurchase bulunamadi: {purchase_id}")
    return purchase


def update_feed_purchase(db: Session, purchase_id: int, data: FeedPurchaseCreate) -> FeedPurchase:
    purchase = get_feed_purchase(db, purchase_id)
    for key, value in data.model_dump().items():
        setattr(purchase, key, value)
    db.commit()
    db.refresh(purchase)
    return purchase


def delete_feed_purchase(db: Session, purchase_id: int) -> None:
    purchase = get_feed_purchase(db, purchase_id)
    db.delete(purchase)
    db.commit()


def list_feed_purchases(db: Session, feed_item_id: int | None = None) -> list[FeedPurchase]:
    stmt = select(FeedPurchase)
    if feed_item_id is not None:
        stmt = stmt.where(FeedPurchase.feed_item_id == feed_item_id)
    return list(db.scalars(stmt.order_by(FeedPurchase.purchase_date.desc())).all())


def _ration_query():
    return select(PenRation).options(joinedload(PenRation.items))


def create_pen_ration(db: Session, data: PenRationCreate) -> PenRation:
    """Yeni bir rasyon donemi baslatir - ayni padogun HALA ACIK (end_date
    NULL) onceki rasyonu varsa, yeni donemin baslangicindan bir gun once
    biterek otomatik kapanir (bkz. app/modules/feed/models.py PenRation).
    Gunluk yem dagitim kaydi YOKTUR - tuketim/maliyet bu donemden istek
    aninda turetilir (bkz. reports/service.py)."""
    open_rations = list(
        db.scalars(select(PenRation).where(PenRation.pen_id == data.pen_id, PenRation.end_date.is_(None))).all()
    )
    for prev in open_rations:
        if data.start_date <= prev.start_date:
            raise ConflictError(
                "Bu padok için zaten daha erken başlayan/aynı tarihte açık bir rasyon var; "
                "yeni rasyonun başlangıç tarihi ondan sonra olmalı."
            )
        prev.end_date = data.start_date - timedelta(days=1)

    ration = PenRation(pen_id=data.pen_id, start_date=data.start_date, note=data.note)
    ration.items = [RationItem(**item.model_dump()) for item in data.items]
    db.add(ration)
    db.commit()
    db.refresh(ration)
    return ration


def get_pen_ration(db: Session, ration_id: int) -> PenRation:
    ration = db.scalars(_ration_query().where(PenRation.id == ration_id)).unique().one_or_none()
    if ration is None:
        raise NotFoundError(f"PenRation bulunamadi: {ration_id}")
    return ration


def update_pen_ration(db: Session, ration_id: int, data: PenRationCreate) -> PenRation:
    """Rasyonun kendisini (donem gecisi degil, hatali girisi) duzeltir -
    onceki rasyonu otomatik kapatma mantigi burada TETIKLENMEZ."""
    ration = get_pen_ration(db, ration_id)
    ration.pen_id = data.pen_id
    ration.start_date = data.start_date
    ration.note = data.note
    ration.items.clear()
    ration.items = [RationItem(**item.model_dump()) for item in data.items]
    db.commit()
    db.refresh(ration)
    return ration


def delete_pen_ration(db: Session, ration_id: int) -> None:
    ration = get_pen_ration(db, ration_id)
    db.delete(ration)
    db.commit()


def list_pen_rations(db: Session, pen_id: int | None = None) -> list[PenRation]:
    stmt = _ration_query()
    if pen_id is not None:
        stmt = stmt.where(PenRation.pen_id == pen_id)
    return list(db.scalars(stmt.order_by(PenRation.start_date.desc())).unique().all())
