from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.feed.models import FeedDistribution, FeedItem
from app.modules.feed.schemas import FeedDistributionCreate, FeedItemCreate


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


def create_feed_distribution(db: Session, data: FeedDistributionCreate) -> FeedDistribution:
    distribution = FeedDistribution(**data.model_dump())
    db.add(distribution)
    db.commit()
    db.refresh(distribution)
    return distribution


def get_feed_distribution(db: Session, distribution_id: int) -> FeedDistribution:
    distribution = db.get(FeedDistribution, distribution_id)
    if distribution is None:
        raise NotFoundError(f"FeedDistribution bulunamadi: {distribution_id}")
    return distribution


def update_feed_distribution(db: Session, distribution_id: int, data: FeedDistributionCreate) -> FeedDistribution:
    distribution = get_feed_distribution(db, distribution_id)
    for key, value in data.model_dump().items():
        setattr(distribution, key, value)
    db.commit()
    db.refresh(distribution)
    return distribution


def delete_feed_distribution(db: Session, distribution_id: int) -> None:
    distribution = get_feed_distribution(db, distribution_id)
    db.delete(distribution)
    db.commit()


def list_feed_distributions(db: Session, pen_id: int | None = None) -> list[FeedDistribution]:
    stmt = select(FeedDistribution)
    if pen_id is not None:
        stmt = stmt.where(FeedDistribution.pen_id == pen_id)
    return list(db.scalars(stmt.order_by(FeedDistribution.distribution_date)).all())
