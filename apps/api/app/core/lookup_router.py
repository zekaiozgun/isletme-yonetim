"""Her lookup/master data tablosu için tam CRUD endpoint'ini tek yerden
üretir (Anayasa m.6: arayüz, seçilebilir alanları bu listelerden doldurur
VE bu listeler artık UI üzerinden yönetilebilir).

Silme, baska kayitlarca referans verilen bir lookup satirini FK RESTRICT
ile engeller (ConflictError -> 409); kaskad silme yoktur.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.core.schemas import LookupCreate, LookupRead


def build_lookup_router(model: type, path: str, tag: str, display_name: str | None = None) -> APIRouter:
    display_name = display_name or model.__tablename__
    router = APIRouter()
    item_path = f"{path}/{{item_id}}"

    def _get_or_404(db: Session, item_id: int):
        item = db.get(model, item_id)
        if item is None:
            raise NotFoundError(f"{model.__tablename__}: {item_id} bulunamadi")
        return item

    @router.get(path, response_model=list[LookupRead], tags=[tag])
    def list_lookup(include_inactive: bool = False, db: Session = Depends(get_db)) -> list:
        stmt = select(model)
        if not include_inactive:
            stmt = stmt.where(model.is_active.is_(True))
        return list(db.scalars(stmt.order_by(model.name)).all())

    @router.post(path, response_model=LookupRead, status_code=201, tags=[tag])
    def create_lookup(payload: LookupCreate, db: Session = Depends(get_db)):
        item = model(**payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @router.get(item_path, response_model=LookupRead, tags=[tag])
    def get_lookup(item_id: int, db: Session = Depends(get_db)):
        return _get_or_404(db, item_id)

    @router.put(item_path, response_model=LookupRead, tags=[tag])
    def update_lookup(item_id: int, payload: LookupCreate, db: Session = Depends(get_db)):
        item = _get_or_404(db, item_id)
        for key, value in payload.model_dump().items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @router.delete(item_path, status_code=204, tags=[tag])
    def delete_lookup(item_id: int, db: Session = Depends(get_db)) -> None:
        item = _get_or_404(db, item_id)
        db.delete(item)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ConflictError(
                f"Bu {display_name} kaydı başka kayıtlar tarafından kullanıldığı için silinemez."
            ) from exc

    return router
