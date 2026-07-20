"""Lookup satirlarini kod ile aramak icin ortak yardimci.

Servis katmani, bir lookup'in serial id'sini asla sabit (hardcoded)
yazmaz - seed sirasina gore degisebilir. Bunun yerine anlamli 'code'
degeri ile arar (orn. "AKTIF", "SATILDI").
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError


def get_lookup_by_code(db: Session, model: type, code: str):
    row = db.scalars(select(model).where(model.code == code)).first()
    if row is None:
        raise NotFoundError(f"{model.__tablename__}: '{code}' kodlu kayit bulunamadi (seed calistirildi mi?)")
    return row
