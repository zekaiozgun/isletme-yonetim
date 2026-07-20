"""Sale servis katmani.

create_sale, Sale kaydini olusturduktan sonra Animal.status_id/status_date
alanlarini 'Satildi' olarak senkronize eder (Anayasa m.8: yasam dongusu
event'lerle izlenir, Animal uzerindeki alanlar bunun anlik yansimasidir).
Gercek kaynak (source of truth) sales tablosudur. update_sale tarih
degisirse senkronu tekrar kurar; delete_sale, satisi geri alir gibi
Animal.status'u 'Aktif'e dondurur.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.lookup_helpers import get_lookup_by_code
from app.modules.animal.lookups import AnimalStatus
from app.modules.animal.models import Animal
from app.modules.animal.service import ACTIVE_STATUS_CODE
from app.modules.sale.models import Buyer, Sale
from app.modules.sale.schemas import BuyerCreate, SaleCreate

SOLD_STATUS_CODE = "SATILDI"


def create_buyer(db: Session, data: BuyerCreate) -> Buyer:
    buyer = Buyer(**data.model_dump())
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


def get_buyer(db: Session, buyer_id: int) -> Buyer:
    buyer = db.get(Buyer, buyer_id)
    if buyer is None:
        raise NotFoundError(f"Buyer bulunamadi: {buyer_id}")
    return buyer


def update_buyer(db: Session, buyer_id: int, data: BuyerCreate) -> Buyer:
    buyer = get_buyer(db, buyer_id)
    for key, value in data.model_dump().items():
        setattr(buyer, key, value)
    db.commit()
    db.refresh(buyer)
    return buyer


def delete_buyer(db: Session, buyer_id: int) -> None:
    buyer = get_buyer(db, buyer_id)
    db.delete(buyer)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu alıcı başka kayıtlar tarafından kullanıldığı için silinemez.") from exc


def list_buyers(db: Session) -> list[Buyer]:
    return list(db.scalars(select(Buyer).order_by(Buyer.name)).all())


def create_sale(db: Session, data: SaleCreate) -> Sale:
    sale = Sale(**data.model_dump())
    db.add(sale)

    sold_status = get_lookup_by_code(db, AnimalStatus, SOLD_STATUS_CODE)
    animal = db.get(Animal, data.animal_id)
    if animal is not None:
        animal.status_id = sold_status.id
        animal.status_date = data.sale_date

    db.commit()
    db.refresh(sale)
    return sale


def get_sale(db: Session, sale_id: int) -> Sale:
    sale = db.get(Sale, sale_id)
    if sale is None:
        raise NotFoundError(f"Sale bulunamadi: {sale_id}")
    return sale


def update_sale(db: Session, sale_id: int, data: SaleCreate) -> Sale:
    sale = get_sale(db, sale_id)
    for key, value in data.model_dump().items():
        setattr(sale, key, value)

    sold_status = get_lookup_by_code(db, AnimalStatus, SOLD_STATUS_CODE)
    animal = db.get(Animal, sale.animal_id)
    if animal is not None:
        animal.status_id = sold_status.id
        animal.status_date = sale.sale_date

    db.commit()
    db.refresh(sale)
    return sale


def delete_sale(db: Session, sale_id: int) -> None:
    sale = get_sale(db, sale_id)
    animal = db.get(Animal, sale.animal_id)
    db.delete(sale)
    db.commit()

    if animal is not None:
        active_status = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE)
        animal.status_id = active_status.id
        animal.status_date = None
        db.commit()


def list_sales(db: Session) -> list[Sale]:
    return list(db.scalars(select(Sale).order_by(Sale.sale_date)).all())
