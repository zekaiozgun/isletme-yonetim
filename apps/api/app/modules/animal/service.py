"""Animal servis katmani: veri girisi + Anayasa m.4/m.5 geregi turetilen
degerler (yas gibi) burada hesaplanir, hicbir zaman DB'de saklanmaz."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.lookup_helpers import get_lookup_by_code
from app.core.validators import require_date_order
from app.modules.animal.lookups import AnimalStatus
from app.modules.animal.models import Animal
from app.modules.animal.schemas import AnimalCreate, CrossbreedRatioEstimateRead, PedigreeNodeRead
from app.modules.auth.schemas import Role
from app.modules.death.models import Death
from app.modules.genetic_resource.models import Sire
from app.modules.sale.models import Sale

DEFAULT_PEDIGREE_GENERATIONS = 4

ACTIVE_STATUS_CODE = "AKTIF"
CANCELLED_ENTRY_STATUS_CODE = "HATALI_GIRIS"


def get_animal_exit_date(db: Session, animal_id: uuid.UUID) -> date | None:
    """Hayvanin SATILDI/OLDU oldugu tarih (yoksa None - hala aktif).
    Sale.animal_id ve Death.animal_id ayri ayri unique oldugundan (bkz.
    _reject_if_already_exited) en fazla biri doludur. Weight/Health/Pen
    modulleri, o hayvana ait yeni bir kaydin cikis tarihinden SONRA
    girilmedigini dogrulamak icin bunu kullanir."""
    sale_date = db.scalars(select(Sale.sale_date).where(Sale.animal_id == animal_id)).first()
    if sale_date is not None:
        return sale_date
    return db.scalars(select(Death.death_date).where(Death.animal_id == animal_id)).first()


def _validate_animal_dates(db: Session, animal: Animal) -> None:
    require_date_order(animal.birth_date, "Doğum tarihi", animal.entry_date, "Giriş tarihi")
    if animal.mother_id is not None:
        mother = db.get(Animal, animal.mother_id)
        if mother is not None:
            require_date_order(mother.birth_date, "Annenin doğum tarihi", animal.birth_date, "Yavrunun doğum tarihi")


def create_animal(db: Session, data: AnimalCreate, created_by_role: Role) -> Animal:
    """Calisan rolu, kaydi cift-onay akisindan gecirdigi icin otomatik
    kilitli (is_locked=True) olusturur - bkz. update_animal."""
    active_status = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE)
    animal = Animal(
        **data.model_dump(),
        status_id=active_status.id,
        status_date=None,
        death_reason_id=None,
        is_locked=(created_by_role == "CALISAN"),
    )
    _validate_animal_dates(db, animal)
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal


def get_animal(db: Session, animal_id: uuid.UUID) -> Animal:
    animal = db.get(Animal, animal_id)
    if animal is None:
        raise NotFoundError(f"Animal bulunamadi: {animal_id}")
    return animal


def update_animal(db: Session, animal_id: uuid.UUID, data: AnimalCreate, requester_role: Role) -> Animal:
    """status_id/status_date/death_reason_id AnimalCreate'te olmadigi icin
    guncellemez - bu alanlar yalnizca Sale/Death event'leriyle degisir.

    Kayit is_locked ise (Calisan'in cift onayla olusturdugu bir kayit),
    yalnizca YONETICI degistirebilir - Calisan icin 409 doner. Duzeltme
    yolu cancel_animal_entry (Hatali Giris Iptali)."""
    animal = get_animal(db, animal_id)
    if animal.is_locked and requester_role != "YONETICI":
        raise ConflictError(
            "Bu hayvan kaydı onaylanmış ve kilitlenmiş; değiştirilemez. "
            "Hatalı giriş ise 'Hatalı Giriş İptali' ile pasife alın."
        )
    for key, value in data.model_dump().items():
        setattr(animal, key, value)
    _validate_animal_dates(db, animal)
    db.commit()
    db.refresh(animal)
    return animal


def cancel_animal_entry(db: Session, animal_id: uuid.UUID, note: str | None = None) -> Animal:
    """'Hatalı Giriş İptali': hem Çalışan hem Yönetici kullanabilir -
    is_locked kontrolü BİLEREK yapılmaz, kilitli bir kaydı düzeltmenin tek
    yolu budur. Sale/Death gibi Animal.status'u değiştiren ayrı bir 'event'
    işlemidir (Anayasa m.8), PUT ile karıştırılmamalı."""
    animal = get_animal(db, animal_id)
    cancelled_status = get_lookup_by_code(db, AnimalStatus, CANCELLED_ENTRY_STATUS_CODE)
    animal.status_id = cancelled_status.id
    animal.status_date = date.today()
    if note:
        animal.note = note
    db.commit()
    db.refresh(animal)
    return animal


def delete_animal(db: Session, animal_id: uuid.UUID) -> None:
    animal = get_animal(db, animal_id)
    db.delete(animal)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Bu hayvan başka kayıtlar (tartı, sağlık, satış, soy vb.) tarafından kullanıldığı için silinemez.") from exc


def list_animals(db: Session, status_id: int | None = None) -> list[Animal]:
    stmt = select(Animal)
    if status_id is not None:
        stmt = stmt.where(Animal.status_id == status_id)
    return list(db.scalars(stmt.order_by(Animal.birth_date, Animal.tag_number)).all())


def calculate_age_in_days(animal: Animal, as_of: date | None = None) -> int | None:
    """Yas, birth_date'ten turetilir; DB'de saklanmaz (Anayasa m.4/m.5)."""
    if animal.birth_date is None:
        return None
    reference_date = as_of or date.today()
    return (reference_date - animal.birth_date).days


def _known_ancestor_node(registry_no: str | None, name: str | None) -> PedigreeNodeRead | None:
    """Dis kaynakli bir boganin KENDI (Sire kaydina bile sahip olmayan,
    sadece kimlik no + ad olarak bilinen) ebeveynini tek bir yaprak dugum
    olarak dondurur - hicbiri girilmemisse None (uydurma bir dugum
    eklenmez, bkz. Sire.known_sire_name docstring'i)."""
    if not registry_no and not name:
        return None
    return PedigreeNodeRead(
        animal_id=None,
        tag_number=registry_no,
        name=name,
        breed_name=None,
        crossbreed_ratio=None,
        is_external=True,
        mother=None,
        father=None,
    )


def _pedigree_node_from_sire(sire: Sire, remaining_generations: int) -> PedigreeNodeRead:
    """Sadece Sire kaydi olarak var olan (suruye ait Animal kaydi OLMAYAN,
    dis kaynakli) bir atayi dondurur. Bu boganin kendi ebeveyni suruye ait
    degildir/tam bir Animal kaydi yoktur, ama katalogda bilinen bir kimlik
    (known_sire_*/known_dam_*) girilmisse - ve derinlik siniri hala
    izin veriyorsa - zincir orada sonlanmaz, bir nesil daha derine iner."""
    mother_node = _known_ancestor_node(sire.known_dam_registry_no, sire.known_dam_name) if remaining_generations > 0 else None
    father_node = _known_ancestor_node(sire.known_sire_registry_no, sire.known_sire_name) if remaining_generations > 0 else None
    return PedigreeNodeRead(
        animal_id=None,
        tag_number=sire.registry_no,
        name=sire.name,
        breed_name=sire.breed.name if sire.breed else None,
        crossbreed_ratio=None,
        is_external=True,
        mother=mother_node,
        father=father_node,
    )


def _build_pedigree_node(db: Session, animal: Animal, remaining_generations: int) -> PedigreeNodeRead:
    """Bir hayvanin kendisini VE (remaining_generations > 0 ise) ebeveyn
    dugumlerini ozyinelemeli olarak insa eder. Anne zinciri Animal.mother_id
    (kendine referans) uzerinden; baba zinciri once Animal.father_sire_id
    (Sire katalogu) uzerinden, suruye ait bir boga ise (Sire.animal_id dolu)
    onun da KENDI Animal kaydina inerek devam eder - boylece baba tarafi da
    anne tarafi kadar derin takip edilebilir. remaining_generations, kotu
    veride (kazara dongu) bile sonsuz ozyinelemeyi imkansiz kilan sabit bir
    derinlik siniridir."""
    mother_node: PedigreeNodeRead | None = None
    father_node: PedigreeNodeRead | None = None

    if remaining_generations > 0:
        if animal.mother_id is not None:
            mother = db.get(Animal, animal.mother_id)
            if mother is not None:
                mother_node = _build_pedigree_node(db, mother, remaining_generations - 1)
        if animal.father_sire_id is not None:
            sire = db.get(Sire, animal.father_sire_id)
            if sire is not None:
                if sire.animal_id is not None:
                    sire_animal = db.get(Animal, sire.animal_id)
                    father_node = (
                        _build_pedigree_node(db, sire_animal, remaining_generations - 1)
                        if sire_animal is not None
                        else _pedigree_node_from_sire(sire, remaining_generations - 1)
                    )
                else:
                    father_node = _pedigree_node_from_sire(sire, remaining_generations - 1)

    return PedigreeNodeRead(
        animal_id=animal.id,
        tag_number=animal.tag_number,
        name=animal.name,
        breed_name=animal.breed.name if animal.breed else None,
        crossbreed_ratio=animal.crossbreed_ratio,
        is_external=False,
        mother=mother_node,
        father=father_node,
    )


def get_pedigree_tree(db: Session, animal_id: uuid.UUID, generations: int = DEFAULT_PEDIGREE_GENERATIONS) -> PedigreeNodeRead:
    """Bir hayvanin kendisinden baslayarak N nesil geriye soy agacini
    dondurur (bkz. _build_pedigree_node). Hicbir yerde SAKLANMAZ - her
    istekte mother_id/father_sire_id zincirinden yeniden kurulur (Anayasa
    m.4/m.5). Kucuk, sabit derinlikli bir agac oldugundan (4 nesil = en
    fazla 15 dugum) toplu on-yukleme yerine dugum basina sorgu yeterlidir."""
    animal = get_animal(db, animal_id)
    return _build_pedigree_node(db, animal, generations)


# --- Melez Orani Tahmini (soy agaci Faz 3) ---
#
# Kural seti (kullanici ile uzerinde mutabik kalinan): her ebeveyn icin
# HEDEF irktan (breed_id) payi uc degerden biridir - BILINEN bir yuzde
# (kendi irki hedefle ayniysa kendi crossbreed_ratio'su), %0 (kendi irki
# FARKLI ama bilinen baska bir irksa - kanitlanmayan bir pay sayilmaz,
# Anayasa m.4) ya da BILINMIYOR (Belirsiz Melez: breed_id=hedef VE
# crossbreed_ratio=None, ya da kendi irki hic bilinmiyor). Iki ebeveynin
# payi da biliniyorsa ortalamalari (bu, hem ilk melezlemeyi/F1'i HEM
# kan temizleme/backcross zincirini AYNI formulle dogru sonuclandirir -
# bkz. kullanici ile yapilan tartisma); sadece biri biliniyorsa onun
# yarisi (ihtiyatli bir ALT SINIR - digeri gercekte daha yuksek olabilir
# ama kanitlanamadigi icin sayilmaz); ikisi de bilinmiyorsa None
# (yavru da Belirsiz Melez kalir, hicbir sayi uydurulmaz).


def _animal_breed_share(animal: Animal, target_breed_id: int) -> Decimal | None:
    if animal.breed_id is None:
        return None
    if animal.breed_id == target_breed_id:
        return animal.crossbreed_ratio  # None ise (Belirsiz Melez) None olarak kalir
    return Decimal("0")


def _father_breed_share(db: Session, father_sire_id: int | None, target_breed_id: int) -> Decimal | None:
    """Baba tarafinin hedef irktan payi. Suruye ait bir boga ise
    (Sire.animal_id dolu) kendi Animal kaydindaki gercek pay kullanilir;
    dis kaynakli bir boga ise (Sire'da ayri bir oran alani YOK) kendi
    breed_id'si HER ZAMAN taniml/bilinen kabul edilir - yani hedefle
    ayniysa %100, farkliysa %0 (Belirsiz Melez durumu dis boga icin
    gecerli degildir, Sire.breed_id zaten zorunlu bir alandir)."""
    if father_sire_id is None:
        return None
    sire = db.get(Sire, father_sire_id)
    if sire is None:
        return None
    if sire.animal_id is not None:
        father_animal = db.get(Animal, sire.animal_id)
        if father_animal is not None:
            return _animal_breed_share(father_animal, target_breed_id)
    return Decimal("100") if sire.breed_id == target_breed_id else Decimal("0")


def estimate_crossbreed_ratio(
    db: Session, mother_id: uuid.UUID | None, father_sire_id: int | None, breed_id: int
) -> CrossbreedRatioEstimateRead:
    """Yeni bir yavrunun, secilen breed_id irkindan tahmini yuzdesini
    dondurur - bkz. modul basindaki kural seti. Hicbir yerde SAKLANMAZ,
    sadece formda ONERI olarak gosterilir; kullanici degistirebilir."""
    mother_share: Decimal | None = None
    if mother_id is not None:
        mother = db.get(Animal, mother_id)
        if mother is not None:
            mother_share = _animal_breed_share(mother, breed_id)
    father_share = _father_breed_share(db, father_sire_id, breed_id)

    if mother_share is not None and father_share is not None:
        ratio = (mother_share + father_share) / 2
        return CrossbreedRatioEstimateRead(
            ratio=ratio, basis="both_known", note="İki ebeveynin de bu ırktan payı biliniyor - ortalaması alındı."
        )
    known_share = mother_share if mother_share is not None else father_share
    if known_share is not None:
        ratio = known_share / 2
        return CrossbreedRatioEstimateRead(
            ratio=ratio,
            basis="one_known_lower_bound",
            note="Sadece bir ebeveynin bu ırktan payı biliniyor - diğeri Belirsiz Melez olduğundan bu, kanıtlanan alt sınırdır (gerçek oran daha yüksek olabilir).",
        )
    return CrossbreedRatioEstimateRead(
        ratio=None, basis="unknown", note="İki ebeveynin de bu ırktan payı bilinmiyor - yavru da Belirsiz Melez kalmalı."
    )
