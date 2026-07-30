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
    """SEED_DATA'daki lookup satirlarini ekler. code zaten varsa VE
    SEED_DATA'daki name farkliysa, kaydin name'i GUNCELLENIR (orn. yazim
    hatasi duzeltmesi - boylece her deploy'da calisan seed, gecmiste
    yanlis yazilmis bir ismi de kendiliginden duzeltir) - ama baska bir
    kaydin (farkli code) zaten kullandigi bir isme CAKISACAKSA guncelleme
    atlanir (LookupMixin name'i unique yaptigi icin). code hic yoksa ve
    name de baska bir kayitta kullanilmiyorsa yeni satir eklenir (ör.
    kullanici UI'dan elle ayni isimde bir kayit eklemisse atlanir).
    """
    for model, rows in seed_data.items():
        existing_rows = list(db.scalars(select(model)).all())
        by_code = {row.code: row for row in existing_rows}
        all_names = {row.name for row in existing_rows}
        for code, name in rows:
            existing = by_code.get(code)
            if existing is not None:
                if existing.name != name and name not in all_names:
                    existing.name = name
                continue
            if name in all_names:
                continue
            db.add(model(code=code, name=name))
    db.commit()
