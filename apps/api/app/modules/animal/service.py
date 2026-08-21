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
from app.modules.animal.schemas import AnimalCreate, PedigreeNodeRead
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


def build_pedigree_tree_for_sire_id(
    db: Session, sire_id: int, generations: int = DEFAULT_PEDIGREE_GENERATIONS
) -> PedigreeNodeRead | None:
    """get_pedigree_tree'nin Sire.id uzerinden calisan hali - dogal asim
    disi (suni tohumlama/sperma partisi uzerinden) bir boga icin soy agaci
    lazim oldugunda (bkz. breeding modulu check_inbreeding) kullanilir.
    Sire bulunamazsa None doner."""
    sire = db.get(Sire, sire_id)
    if sire is None:
        return None
    if sire.animal_id is not None:
        sire_animal = db.get(Animal, sire.animal_id)
        if sire_animal is not None:
            return _build_pedigree_node(db, sire_animal, generations)
    return _pedigree_node_from_sire(sire, generations)


def _collect_pedigree_keys(node: PedigreeNodeRead | None, keys: dict[tuple, str]) -> None:
    """Bir soy agacindaki HER dugumu (kok dahil) benzersiz bir anahtarla
    (surudeki bir hayvansa animal_id, dis kaynakli bir atasysa kupe/kayit
    no + ad ikilisi) bir sozluge toplar - bkz. find_common_ancestors."""
    if node is None:
        return
    key = (node.animal_id,) if node.animal_id is not None else (node.tag_number, node.name)
    if key != (None, None):
        keys.setdefault(key, node.tag_number or node.name or "?")
    _collect_pedigree_keys(node.mother, keys)
    _collect_pedigree_keys(node.father, keys)


def find_common_ancestors(tree_a: PedigreeNodeRead, tree_b: PedigreeNodeRead) -> list[str]:
    """Iki soy agacinda ORTAK olan atalari bulur - KOK dugumler DAHIL
    (biri digerinin dogrudan atasiysa - orn. baba-kiz - da yakalanir).
    Sadece GORUNTULEME icin isim listesi doner, hicbir yerde saklanmaz;
    kullanici uyariyi gorup KENDI karar verir, sistem hicbir seyi
    engellemez (bkz. breeding modulu check_inbreeding)."""
    keys_a: dict[tuple, str] = {}
    keys_b: dict[tuple, str] = {}
    _collect_pedigree_keys(tree_a, keys_a)
    _collect_pedigree_keys(tree_b, keys_b)
    common_keys = set(keys_a) & set(keys_b)
    return sorted({keys_a[k] for k in common_keys})


# --- Genetik Karma (soy agaci Faz 6) ---
#
# crossbreed_ratio artik elle girilen bir alan DEGIL (Faz 3'un aksine -
# bkz. kullanici geri bildirimi: bu, Anayasa m.4/m.5'e aykiriydi, bir
# fact degil bir turetimdi). Bunun yerine soy agacindaki (mother_id/
# father_sire_id zinciri) HER atanin breed_id'si - zaten girilen gercek
# bir fact - nesil derinligine gore agirliklandirilip toplanir: ebeveyn
# %50, buyukanne/dede %25, ... Zincir nerede biterse (bir ebeveyn TARAFI
# bilinmiyor ya da DEFAULT_PEDIGREE_GENERATIONS derinligine ulasildi) o
# TARAFA dusen pay, o hayvanin KENDI breed_id'si (varsa) ile doldurulur -
# satin alinan (anne/babasi hic bilinmeyen) hayvanlar icin bu, satin
# alirken kaydedilen Irk'in zaten gercek bir fact oldugu varsayimina
# dayanir. breed_id de yoksa o pay sozlukte hic gorunmez - cagiran taraf
# (bkz. reports/service.py list_genetic_composition) bilinen paylarin
# toplamini 100'den cikarip "Belirsiz" kismini bulur, hicbir sayi
# uydurulmaz.


def _sire_breed_composition(
    db: Session, father_sire_id: int | None, weight: Decimal, remaining_generations: int
) -> dict[int, Decimal]:
    if father_sire_id is None:
        return {}
    sire = db.get(Sire, father_sire_id)
    if sire is None:
        return {}
    if sire.animal_id is not None:
        return _animal_breed_composition(db, sire.animal_id, weight, remaining_generations)
    # Dis kaynakli boga: kendi ebeveyni suruye ait degil, known_sire_*/
    # known_dam_* alanlari da sadece KIMLIK tasir (irk tasimaz) - zincir
    # burada biter, boganin kendi (zorunlu) breed_id'si tam agirlikla sayilir.
    return {sire.breed_id: weight} if sire.breed_id is not None else {}


def _animal_breed_composition(
    db: Session, animal_id: uuid.UUID | None, weight: Decimal, remaining_generations: int
) -> dict[int, Decimal]:
    """Bir hayvanin agirlikli irk dagilimi - {breed_id: pay} sozlugu,
    toplami eksik soy nedeniyle 100'den KUCUK olabilir (bkz. modul basi
    aciklamasi). remaining_generations, get_pedigree_tree ile AYNI sabit
    derinlik sinirini (DEFAULT_PEDIGREE_GENERATIONS) kullanir - kotu
    veride (kazara dongu) bile sonsuz ozyinelemeyi imkansiz kilar."""
    if animal_id is None:
        return {}
    animal = db.get(Animal, animal_id)
    if animal is None:
        return {}
    own_breed = {animal.breed_id: weight} if animal.breed_id is not None else {}
    if remaining_generations <= 0 or (animal.mother_id is None and animal.father_sire_id is None):
        return own_breed

    half = weight / 2
    own_half = {animal.breed_id: half} if animal.breed_id is not None else {}
    mother_share = (
        _animal_breed_composition(db, animal.mother_id, half, remaining_generations - 1)
        if animal.mother_id is not None
        else own_half
    )
    father_share = (
        _sire_breed_composition(db, animal.father_sire_id, half, remaining_generations - 1)
        if animal.father_sire_id is not None
        else own_half
    )
    result: dict[int, Decimal] = {}
    for source in (mother_share, father_share):
        for breed_id, share in source.items():
            result[breed_id] = result.get(breed_id, Decimal("0")) + share
    return result


def get_animal_genetic_composition(db: Session, animal_id: uuid.UUID) -> dict[int, Decimal]:
    """Bir hayvanin soy agacindaki (en fazla DEFAULT_PEDIGREE_GENERATIONS
    nesil geriye) HER irkin toplam payini dondurur - bkz. modul basi
    aciklamasi. Hicbir yerde SAKLANMAZ, istek aninda turetilir (Anayasa
    m.4/m.5)."""
    return _animal_breed_composition(db, animal_id, Decimal("100"), DEFAULT_PEDIGREE_GENERATIONS)
