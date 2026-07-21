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


def seed_lookup_rows(db: Session, seed_data: dict[type, list[tuple[str, str]]]) -> None:
    """SEED_DATA'daki lookup satirlarini ekler; code veya name zaten
    varsa (ör. kullanıcı UI'dan elle ayni isimde bir kayit eklemisse)
    o satiri atlar. LookupMixin hem code hem name'i unique yaptigi icin
    ikisi de kontrol edilmeli - yoksa tekil kisit ihlali tum seed
    islemini (ve dolayisiyla container baslangicini) patlatir.
    """
    for model, rows in seed_data.items():
        existing_codes = {code for (code,) in db.query(model.code).all()}
        existing_names = {name for (name,) in db.query(model.name).all()}
        for code, name in rows:
            if code in existing_codes or name in existing_names:
                continue
            db.add(model(code=code, name=name))
    db.commit()
