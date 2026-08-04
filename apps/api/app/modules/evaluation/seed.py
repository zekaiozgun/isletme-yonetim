"""Master Data icin baslangic referans verileri.

Calistirma: python -m app.modules.evaluation.seed

_seed_reasons ORM sinifi (EvaluationReason) yerine bilincli olarak HAM SQL
kullanir: EvaluationReason, models.py'de AnimalEvaluation ile AYNI dosyada
tanimli - onu import etmek AnimalEvaluation mapper'ini da (relationship("Animal")
ile) SQLAlchemy registry'sine kaydeder. seed_all.py sadece her modulun
lookups.py'sini (Animal'a hicbir referansi olmayan salt LookupMixin
siniflarini) import ettigi icin Animal sinifi bu surecte hic yuklenmez;
AnimalEvaluation mapper'i configure_mappers() sirasinda "Animal" adini
cozemeyip hata verir (bkz. diger tum seed.py dosyalarinin AYNI nedenle
kendi models.py'lerini degil sadece lookups.py'lerini import etmesi).
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.lookup_helpers import get_lookup_by_code, seed_lookup_rows
from app.modules.evaluation.lookups import EvaluationDirection, EvaluationPriority

CULLING_DIRECTION_CODE = "SURUDEN_CIKARMA"
BREEDING_DIRECTION_CODE = "DAMIZLIK_ONERISI"

SEED_DATA: dict[type, list[tuple[str, str]]] = {
    EvaluationDirection: [
        (CULLING_DIRECTION_CODE, "Sürüden Çıkarma"),
        (BREEDING_DIRECTION_CODE, "Damızlık Önerisi"),
    ],
    EvaluationPriority: [
        ("DUSUK", "Düşük"),
        ("ORTA", "Orta"),
        ("YUKSEK", "Yüksek"),
    ],
}

# (code, name, direction_code) - EvaluationReason'in direction_id FK'si
# oldugu icin seed_lookup_rows'un (code, name) ciftleriyle calisan genel
# mekanizmasina uymuyor, burada ayrica ele alinir.
REASON_SEED_DATA: list[tuple[str, str, str]] = [
    ("DUSUK_VERIM", "Düşük Verim", CULLING_DIRECTION_CODE),
    ("YASLILIK", "Yaşlılık", CULLING_DIRECTION_CODE),
    ("FERTILITE_SORUNU", "Fertilite Sorunu", CULLING_DIRECTION_CODE),
    ("SAGLIK_YAPISAL_SORUN", "Sağlık/Yapısal Sorun", CULLING_DIRECTION_CODE),
    ("SURU_YENILEME", "Sürü Yenileme", CULLING_DIRECTION_CODE),
    ("CIKARMA_DIGER", "Diğer (Çıkarma)", CULLING_DIRECTION_CODE),
    ("USTUN_BUYUME", "Üstün Büyüme Performansı", BREEDING_DIRECTION_CODE),
    ("USTUN_GENETIK", "Üstün Genetik/Soy Değeri", BREEDING_DIRECTION_CODE),
    ("YUKSEK_DOL_VERIMI", "Yüksek Döl Verimi", BREEDING_DIRECTION_CODE),
    ("DAMIZLIK_DIGER", "Diğer (Damızlık)", BREEDING_DIRECTION_CODE),
]


def _seed_reasons(db: Session) -> None:
    existing = db.execute(text("SELECT code, name FROM evaluation_reasons")).all()
    by_code = {row.code: row.name for row in existing}
    all_names = set(by_code.values())
    for code, name, direction_code in REASON_SEED_DATA:
        direction_id = get_lookup_by_code(db, EvaluationDirection, direction_code).id
        if code in by_code:
            if by_code[code] != name and name not in all_names:
                db.execute(
                    text("UPDATE evaluation_reasons SET name = :name WHERE code = :code"),
                    {"name": name, "code": code},
                )
            continue
        if name in all_names:
            continue
        db.execute(
            text(
                "INSERT INTO evaluation_reasons (code, name, direction_id, is_active, created_at, updated_at) "
                "VALUES (:code, :name, :direction_id, true, now(), now())"
            ),
            {"code": code, "name": name, "direction_id": direction_id},
        )
    db.commit()


def run(db: Session) -> None:
    seed_lookup_rows(db, SEED_DATA)
    _seed_reasons(db)


def main() -> None:
    db = SessionLocal()
    try:
        run(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
