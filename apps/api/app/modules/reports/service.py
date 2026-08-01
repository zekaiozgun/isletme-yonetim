"""Raporlama servis katmani.

Anayasa m.5: tum hesaplamalar (yas, gun farki, beklenen dogum tarihi vb.)
istek aninda burada turetilir, hicbir yerde saklanmaz. Anayasa m.7/m.8
geregi ayri bir "dogum/calving" event tablosu yoktur - bir hayvanin
dogurup dogurmadigi, kendisine mother_id ile bagli baska bir Animal
kaydinin (buzaginin) var olup olmadigina bakilarak turetilir.

Her aktif disi hayvan, su bes durumdan TAM OLARAK BIRINE duser (cakisma
yoktur, bkz. asagidaki _classify_female):
  1) Hic tohumlanmamis + yas >= BREEDING_AGE_MONTHS  -> Tohumlanacak (ilk)
  2) Son dogumu son tohumlamasindan sonra + gun farki >= POSTPARTUM_WAIT_DAYS
     -> Tohumlanacak (dogum sonrasi)
  3) Aktif tohumlama dongusu, kontrol yok ya da SUPHELI -> Tohumlu (bekliyor)
  4) Aktif tohumlama dongusu, sonuc GEBE -> Gebe (+ Tohumlu listesinde de gorunur)
  5) Aktif tohumlama dongusu, sonuc BOS -> Tekrar Kizginlik / Bos Cikan
     (+ Tohumlanacak Hayvanlar listesinde de gorunur - tekrar tohumlanmasi gereken bir hayvan)
"""

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased, joinedload

from app.core.date_utils import full_months_between
from app.core.lookup_helpers import get_lookup_by_code
from app.modules.animal.lookups import AnimalStatus, EntrySource, Gender
from app.modules.animal.models import Animal
from app.modules.breeding.lookups import PregnancyResult
from app.modules.breeding.models import BreedingEvent, PregnancyCheck
from app.modules.genetic_resource.models import SemenBatch, Sire
from app.modules.death.models import Death
from app.modules.feed.models import FeedItem, FeedPurchase, PenRation, RationItem
from app.modules.fx import service as fx_service
from app.modules.health.models import HealthEvent
from app.modules.sale.models import Sale
from app.modules.valuation.models import GrowthValuationCheckpoint
from app.modules.weight.models import WeightRecord
from app.modules.pen.models import Pen, PenAssignment
from app.modules.reports.schemas import (
    AnimalMarketValueRead,
    AnimalProfitabilityRead,
    BredAnimalRead,
    BreedingCandidateRead,
    BreedingPerformanceRead,
    CalvingIntervalRead,
    CalvingRead,
    DashboardSummaryRead,
    DeathLossReportRead,
    FeedConsumptionRead,
    FeedStockStatusRead,
    HealthEventReportRead,
    HerdCostSummaryRead,
    HerdFlowReportRead,
    HerdInventoryRead,
    HerdStatusSummaryRead,
    OffspringByMotherRead,
    OffspringBySireRead,
    PenEfficiencyRead,
    PenOccupancyRead,
    PregnancyCheckResultRead,
    SalesReportRead,
    WeightGainRead,
    WithdrawalPeriodRead,
    YoungAnimalRead,
)

FEMALE_GENDER_CODE = "DISI"
MALE_GENDER_CODE = "ERKEK"
ACTIVE_STATUS_CODE = "AKTIF"
DIFFICULT_BIRTH_TYPE_CODE = "GUC"
ILLNESS_EVENT_TYPE_CODE = "HASTALIK_BILDIRIMI"
FEED_TON_UNIT_CODE = "TON"
FEED_GRAM_UNIT_CODE = "GR"


def _to_kg(quantity: Decimal, unit_code: str) -> float:
    """Yem miktarini kg'a normalize eder (ton kayitlari x1000, gram kayitlari /1000)."""
    if unit_code == FEED_TON_UNIT_CODE:
        return float(quantity) * 1000
    if unit_code == FEED_GRAM_UNIT_CODE:
        return float(quantity) / 1000
    return float(quantity)


def _feed_avg_cost_per_kg(db: Session, feed_item_id: int, as_of_date: date) -> Decimal | None:
    """Bir yem kaleminin as_of_date'e kadarki (dahil) TUM alimlarindan
    turetilen agirlikli ortalama birim maliyeti (TL/kg) - hicbir yerde
    saklanmaz; hem rasyon/tuketim maliyetinde hem stok degerinde kullanilir
    (Anayasa m.4: birim fiyat elle girilmez, fatura tutarindan turetilir).
    Maliyetli hic alim yoksa None doner."""
    purchases = db.scalars(
        select(FeedPurchase)
        .options(joinedload(FeedPurchase.unit))
        .where(
            FeedPurchase.feed_item_id == feed_item_id,
            FeedPurchase.purchase_date <= as_of_date,
            FeedPurchase.total_cost.isnot(None),
        )
    ).all()
    total_cost = Decimal("0")
    total_kg = Decimal("0")
    for purchase in purchases:
        total_cost += purchase.total_cost
        total_kg += Decimal(str(_to_kg(purchase.quantity, purchase.unit.code)))
    if total_kg == 0:
        return None
    return total_cost / total_kg


def _daily_headcounts(assignments: list[PenAssignment], start: date, end: date) -> dict[date, int]:
    """Onceden (bir padoga gore) cekilmis PenAssignment listesinden,
    [start, end] arasindaki her gun icin o padokta kayitli hayvan sayisini
    Python'da hesaplar (gun basina DB sorgusu atmaz)."""
    counts: dict[date, int] = {}
    day = start
    while day <= end:
        counts[day] = sum(
            1 for a in assignments if a.assigned_date <= day and (a.removed_date is None or a.removed_date >= day)
        )
        day += timedelta(days=1)
    return counts


def _overlap_days_count(start_a: date, end_a: date, start_b: date, end_b: date) -> int:
    start = max(start_a, start_b)
    end = min(end_a, end_b)
    return (end - start).days + 1 if end >= start else 0


BREEDING_AGE_MONTHS = 12
POSTPARTUM_WAIT_DAYS = 45
PREGNANCY_CHECK_DUE_DAYS = 45
CALF_MAX_MONTHS = 7

CONFIRMED_PREGNANCY_RESULT_CODE = "GEBE"
PURCHASE_ENTRY_SOURCE_CODE = "SATIN_ALMA"
# Demirbas (inek/damizlik boga) amortisman parametreleri - USD bazinda
# (TL enflasyonundan etkilenmesin diye, bkz. _asset_book_value).
DEPRECIATION_USEFUL_LIFE_YEARS = 10
DEPRECIATION_RESIDUAL_RATIO = Decimal("0.5")
GESTATION_DAYS = 283

# Buyume degerleme cipalari (bkz. app/modules/valuation) - ay -> gun
# yaklasik donusumu, sadece iki cipa arasi lineer interpolasyonun GUNLUK
# granulerlikte puruzsuz olmasi icin (takvim ay uzunlugu degil, sabit bir
# yaklasiklik - full_months_between'in aksine burada kesirli gun onemli).
GROWTH_CHECKPOINT_DAYS_PER_MONTH = 30


def _latest_breeding_by_dam(db: Session) -> dict[uuid.UUID, BreedingEvent]:
    stmt = select(BreedingEvent).options(joinedload(BreedingEvent.service_method)).order_by(BreedingEvent.service_date)
    latest: dict[uuid.UUID, BreedingEvent] = {}
    for event in db.scalars(stmt).all():
        latest[event.dam_id] = event  # siralamadan dolayi son atama en yeni olur
    return latest


def _returned_from_pregnancy(
    db: Session, dam_id: uuid.UUID, current_service_date: date, since: date | None
) -> bool:
    """Bu hayvanin, MEVCUT (degerlendirilen) tohumlama kaydindan ONCE - ayni
    üreme döngüsü içinde (son doğumundan bu yana) - başka bir tohumlama
    kaydında onaylanmış (GEBE) bir gebelik kontrolü var mıydı? Varsa, yeni
    tohumlama o eski onaylı gebeliğin artık geçerli olmadığını ima eder.
    Sistem SEBEBİ (düşük mü, yanlış giriş mi) TAHMİN ETMEZ (Anayasa m.4) -
    sadece bu çelişkiyi görünür kılar, gerçek sebebi kullanıcı not alanına
    kendisi kaydeder."""
    stmt = (
        select(func.count(PregnancyCheck.id))
        .select_from(PregnancyCheck)
        .join(BreedingEvent, PregnancyCheck.breeding_event_id == BreedingEvent.id)
        .join(PregnancyResult, PregnancyCheck.result_id == PregnancyResult.id)
        .where(
            BreedingEvent.dam_id == dam_id,
            BreedingEvent.service_date < current_service_date,
            PregnancyResult.code == CONFIRMED_PREGNANCY_RESULT_CODE,
        )
    )
    if since is not None:
        stmt = stmt.where(BreedingEvent.service_date > since)
    return (db.scalar(stmt) or 0) > 0


def _latest_calving_by_dam(db: Session) -> dict[uuid.UUID, date]:
    stmt = (
        select(Animal.mother_id, func.max(Animal.birth_date))
        .where(Animal.mother_id.isnot(None), Animal.birth_date.isnot(None))
        .group_by(Animal.mother_id)
    )
    return {mother_id: birth_date for mother_id, birth_date in db.execute(stmt).all()}


def _service_attempt_count(db: Session, dam_id: uuid.UUID, since: date | None) -> int:
    """Bir hayvanin mevcut üreme döngüsünde (son doğumundan -hiç
    doğurmadıysa hiçbir sınır olmadan- bugüne kadar) kaç kez tohumlandığını
    sayar - gebelik gerçekleşmeden tekrarlanan denemeleri görmek için
    (fertilite sorunu belirtisi olabilir)."""
    stmt = select(func.count(BreedingEvent.id)).where(BreedingEvent.dam_id == dam_id)
    if since is not None:
        stmt = stmt.where(BreedingEvent.service_date > since)
    return db.scalar(stmt) or 0


def _latest_check_by_event(db: Session) -> dict[int, PregnancyCheck]:
    stmt = select(PregnancyCheck).options(joinedload(PregnancyCheck.result)).order_by(PregnancyCheck.check_date)
    latest: dict[int, PregnancyCheck] = {}
    for check in db.scalars(stmt).all():
        latest[check.breeding_event_id] = check
    return latest


@dataclass
class _Classification:
    kind: str  # "candidate_new" | "postpartum_waiting" | "candidate_postpartum" | "pending" | "suspicious" | "pregnant" | "open" | "none"
    breeding_event: BreedingEvent | None = None
    last_calving_date: date | None = None
    # En son gebelik kontrolunun notu (varsa) - bkz. PregnancyCheck.note.
    check_note: str | None = None


def _classify_female(
    animal: Animal,
    last_breed: BreedingEvent | None,
    last_calving: date | None,
    latest_check_by_event: dict[int, PregnancyCheck],
    today: date,
) -> _Classification:
    if last_breed is None:
        if last_calving is None:
            age_months = full_months_between(animal.birth_date, today) if animal.birth_date else None
            if age_months is not None and age_months >= BREEDING_AGE_MONTHS:
                return _Classification(kind="candidate_new")
            return _Classification(kind="none")
        # Hic tohumlama kaydi girilmeden dogurmus (orn. gebe/laktasyondaki bir
        # hayvan disaridan alinmis) - yine de dogum sonrasi kuralini uygula.
        days_since_calving = (today - last_calving).days
        if days_since_calving >= POSTPARTUM_WAIT_DAYS:
            return _Classification(kind="candidate_postpartum", last_calving_date=last_calving)
        return _Classification(kind="postpartum_waiting", last_calving_date=last_calving)

    if last_calving is not None and last_calving > last_breed.service_date:
        days_since_calving = (today - last_calving).days
        if days_since_calving >= POSTPARTUM_WAIT_DAYS:
            return _Classification(kind="candidate_postpartum", last_calving_date=last_calving)
        return _Classification(kind="postpartum_waiting", last_calving_date=last_calving)

    check = latest_check_by_event.get(last_breed.id)
    if check is None:
        return _Classification(kind="pending", breeding_event=last_breed)
    result_code = check.result.code
    if result_code == "GEBE":
        return _Classification(kind="pregnant", breeding_event=last_breed, check_note=check.note)
    if result_code == "BOS":
        return _Classification(kind="open", breeding_event=last_breed, check_note=check.note)
    return _Classification(kind="suspicious", breeding_event=last_breed, check_note=check.note)


def _active_females(db: Session) -> list[Animal]:
    female_id = get_lookup_by_code(db, Gender, FEMALE_GENDER_CODE).id
    active_id = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE).id
    stmt = select(Animal).where(Animal.gender_id == female_id, Animal.status_id == active_id)
    return list(db.scalars(stmt.order_by(Animal.tag_number)).all())


def _classify_all_active_females(db: Session, today: date) -> list[tuple[Animal, _Classification]]:
    last_breeding = _latest_breeding_by_dam(db)
    last_calving = _latest_calving_by_dam(db)
    latest_checks = _latest_check_by_event(db)
    results: list[tuple[Animal, _Classification]] = []
    for animal in _active_females(db):
        classification = _classify_female(
            animal, last_breeding.get(animal.id), last_calving.get(animal.id), latest_checks, today
        )
        results.append((animal, classification))
    return results


_BREEDING_CANDIDATE_REASONS = {
    "candidate_new": "İlk Tohumlama",
    "candidate_postpartum": "Tohumlanacak",
    "open": "Tekrar Kızgınlık / Boş",
    # Dogum sonrasi bekleme suresini (POSTPARTUM_WAIT_DAYS) henuz
    # tamamlamamis, dolayisiyla henuz tohumlanmaya hazir OLMAYAN hayvanlar -
    # sadece bilgi amacli gorunur (aksiyon gerektirmez), bu yuzden dashboard
    # ozetindeki breeding_candidate_count'a dahil edilmez (bkz. get_dashboard_summary).
    "postpartum_waiting": "Post Partum",
}
_BREEDING_CANDIDATE_REASON_ORDER = {"candidate_new": 0, "candidate_postpartum": 1, "open": 2, "postpartum_waiting": 3}


def list_breeding_candidates(db: Session, today: date | None = None) -> list[BreedingCandidateRead]:
    """"Tekrar Kızgınlık / Boş Çıkanlar" burada AYRI bir rapor değildir -
    dört aday türünden biri (reason="Tekrar Kızgınlık / Boş") olarak bu
    listenin içindedir; eskiden ayrı bir rapor olarak da sunuluyordu ama
    bu listenin birebir alt kümesi olduğundan (aynı hayvanlar, aynı sebep)
    tek rapora birleştirildi - o rapora özgü days_open/service_method_name
    alanları sadece bu reason'da dolar.

    Doğum yapan TÜM hayvanlar bu listede görünür - doğum sonrası bekleme
    süresini (POSTPARTUM_WAIT_DAYS, 45 gün) henüz tamamlamamışlar
    reason="Post Partum" ile (henüz aksiyon gerektirmez, bilgi amaçlıdır),
    tamamlamış olanlar reason="Tohumlanacak" ile görünür (bkz. _classify_female)."""
    today = today or date.today()
    last_calving_by_dam = _latest_calving_by_dam(db)
    entries: list[tuple[int, BreedingCandidateRead]] = []
    for animal, classification in _classify_all_active_females(db, today):
        if classification.kind not in _BREEDING_CANDIDATE_REASONS:
            continue
        last_service_date = None
        days_open = None
        service_method_name = None
        returned_from_pregnancy = False
        if classification.kind == "open":
            assert classification.breeding_event is not None
            last_service_date = classification.breeding_event.service_date
            days_open = (today - last_service_date).days
            service_method_name = classification.breeding_event.service_method.name
            returned_from_pregnancy = _returned_from_pregnancy(
                db, animal.id, last_service_date, last_calving_by_dam.get(animal.id)
            )
        attempt_count = _service_attempt_count(db, animal.id, last_calving_by_dam.get(animal.id))
        row = BreedingCandidateRead(
            animal_id=animal.id,
            tag_number=animal.tag_number,
            name=animal.name,
            birth_date=animal.birth_date,
            age_months=full_months_between(animal.birth_date, today) if animal.birth_date else None,
            reason=_BREEDING_CANDIDATE_REASONS[classification.kind],
            reason_code=classification.kind,
            last_calving_date=classification.last_calving_date,
            last_service_date=last_service_date,
            days_open=days_open,
            service_method_name=service_method_name,
            service_attempt_count=attempt_count,
            returned_from_pregnancy=returned_from_pregnancy,
            note=classification.check_note,
        )
        entries.append((_BREEDING_CANDIDATE_REASON_ORDER[classification.kind], row))

    def sort_key(entry: tuple[int, BreedingCandidateRead]) -> tuple[int, object]:
        order, row = entry
        # Her grup icinde en uzun süredir bekleyen üstte: "Boş Çıkan"da en
        # uzun açık süre, "Tohumlanacak"/"Post Partum"da en eski son doğum
        # tarihi (en cok gun once dogurmus), "İlk Tohumlama"da en yaşlı
        # (en yuksek yas) hayvan.
        if row.days_open is not None:
            return (order, -row.days_open)
        if row.last_calving_date is not None:
            return (order, row.last_calving_date)
        if row.age_months is not None:
            return (order, -row.age_months)
        return (order, row.tag_number)

    entries.sort(key=sort_key)
    return [row for _, row in entries]


def list_bred_animals(db: Session, today: date | None = None) -> list[BredAnimalRead]:
    today = today or date.today()
    last_calving_by_dam = _latest_calving_by_dam(db)
    rows: list[BredAnimalRead] = []
    for animal, classification in _classify_all_active_females(db, today):
        if classification.kind not in ("pending", "suspicious", "pregnant"):
            continue
        event = classification.breeding_event
        assert event is not None
        days_since_service = (today - event.service_date).days
        if classification.kind == "pending":
            check_status = "Tohumlu"
            check_due = days_since_service >= PREGNANCY_CHECK_DUE_DAYS
        elif classification.kind == "suspicious":
            check_status = "Şüpheli"
            check_due = True
        else:
            check_status = "Gebe"
            check_due = False
        # Kontrol sonucu ne olursa olsun (henuz onaylanmamis olsa bile)
        # servis tarihinden turetilen bir projeksiyon - Gebe disindaki
        # satirlarda "tahmini" niteliktedir.
        expected_calving = event.service_date + timedelta(days=GESTATION_DAYS)
        rows.append(
            BredAnimalRead(
                breeding_event_id=event.id,
                animal_id=animal.id,
                tag_number=animal.tag_number,
                name=animal.name,
                service_date=event.service_date,
                service_method_name=event.service_method.name,
                days_since_service=days_since_service,
                check_status=check_status,
                pregnancy_check_due=check_due,
                expected_calving_date=expected_calving,
                days_until_calving=(expected_calving - today).days,
                service_attempt_count=_service_attempt_count(db, animal.id, last_calving_by_dam.get(animal.id)),
                returned_from_pregnancy=_returned_from_pregnancy(
                    db, animal.id, event.service_date, last_calving_by_dam.get(animal.id)
                ),
                note=classification.check_note,
            )
        )

    def sort_key(row: BredAnimalRead) -> tuple[int, object]:
        if row.pregnancy_check_due and row.check_status != "Gebe":
            return (0, -row.days_since_service)
        if row.check_status == "Tohumlu":
            return (1, row.service_date)
        if row.check_status == "Gebe":
            return (2, row.service_date)
        return (3, row.service_date)

    rows.sort(key=sort_key)
    return rows



def list_active_withdrawal_periods(db: Session, today: date | None = None) -> list[WithdrawalPeriodRead]:
    """Su anda ilac arinma suresi devam eden (satisa/kesime henuz hazir
    olmayan) aktif hayvanlar. withdrawal_end_date DB'de saklanmaz, her
    saglik olayinda event_date + medication.withdrawal_period_days olarak
    hesaplanir (bkz. app.modules.health.service.calculate_withdrawal_end_date
    - ayni formul, burada raporlama icin toplu calistirilir)."""
    today = today or date.today()
    active_id = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE).id
    stmt = (
        select(HealthEvent)
        .join(Animal, HealthEvent.animal_id == Animal.id)
        .options(joinedload(HealthEvent.animal), joinedload(HealthEvent.medication))
        .where(Animal.status_id == active_id, HealthEvent.medication_id.isnot(None))
    )
    rows: list[WithdrawalPeriodRead] = []
    for event in db.scalars(stmt).all():
        medication = event.medication
        if medication is None or medication.withdrawal_period_days <= 0:
            continue
        withdrawal_end = event.event_date + timedelta(days=medication.withdrawal_period_days)
        if withdrawal_end < today:
            continue
        rows.append(
            WithdrawalPeriodRead(
                animal_id=event.animal_id,
                tag_number=event.animal.tag_number,
                medication_name=medication.name,
                event_date=event.event_date,
                withdrawal_end_date=withdrawal_end,
                days_remaining=(withdrawal_end - today).days,
            )
        )
    rows.sort(key=lambda r: r.days_remaining)
    return rows


def list_calvings(db: Session, start_date: date, end_date: date) -> list[CalvingRead]:
    """Belirtilen tarih araliginda dogan (birth_date) tum hayvanlar - dogum/buzagilama
    raporu. Anayasa m.7/m.8 geregi ayri bir calving event tablosu yok; bir dogum,
    kendisi de bir Animal kaydi olan buzaginin birth_date'i uzerinden turetilir."""
    stmt = (
        select(Animal)
        .options(
            joinedload(Animal.gender),
            joinedload(Animal.birth_type),
            joinedload(Animal.litter_type),
            joinedload(Animal.mother),
            joinedload(Animal.father_sire),
            joinedload(Animal.status),
        )
        .where(Animal.birth_date.isnot(None), Animal.birth_date >= start_date, Animal.birth_date <= end_date)
        .order_by(Animal.birth_date, Animal.tag_number)
    )
    rows: list[CalvingRead] = []
    for animal in db.scalars(stmt).all():
        assert animal.birth_date is not None
        rows.append(
            CalvingRead(
                animal_id=animal.id,
                tag_number=animal.tag_number,
                name=animal.name,
                birth_date=animal.birth_date,
                gender_name=animal.gender.name,
                birth_type_name=animal.birth_type.name if animal.birth_type else None,
                is_difficult_birth=bool(animal.birth_type and animal.birth_type.code == DIFFICULT_BIRTH_TYPE_CODE),
                litter_type_name=animal.litter_type.name if animal.litter_type else None,
                birth_weight_kg=animal.birth_weight_kg,
                mother_id=animal.mother_id,
                mother_tag_number=animal.mother.tag_number if animal.mother else None,
                father_sire_name=animal.father_sire.name if animal.father_sire else None,
                status_name=animal.status.name,
                note=animal.note,
            )
        )
    return rows


def list_offspring_by_mother(db: Session) -> list[OffspringByMotherRead]:
    """Anne bazinda yavru (soy) listesi - mother_id dolu olan TUM hayvanlar,
    guncel durumlari ne olursa olsun (satilmis/olmus yavrular da dahildir,
    cunku bu bir soy kaydidir, aktif suru listesi degildir). Anne kupe
    numarasina, sonra dogum tarihine gore siralanir - boylece ayni anneden
    gelen yavrular listede ardisik gorunur."""
    mother_alias = aliased(Animal)
    stmt = (
        select(Animal)
        .join(mother_alias, Animal.mother_id == mother_alias.id)
        .options(joinedload(Animal.mother), joinedload(Animal.gender), joinedload(Animal.status))
        .where(Animal.mother_id.isnot(None), Animal.birth_date.isnot(None))
        .order_by(mother_alias.tag_number, Animal.birth_date)
    )
    rows: list[OffspringByMotherRead] = []
    for animal in db.scalars(stmt).all():
        assert animal.mother is not None and animal.birth_date is not None
        rows.append(
            OffspringByMotherRead(
                mother_id=animal.mother_id,
                mother_tag_number=animal.mother.tag_number,
                animal_id=animal.id,
                tag_number=animal.tag_number,
                name=animal.name,
                birth_date=animal.birth_date,
                gender_name=animal.gender.name,
                status_name=animal.status.name,
            )
        )
    return rows


def list_offspring_by_sire(db: Session) -> list[OffspringBySireRead]:
    """Baba bazinda yavru (soy) listesi - father_sire_id dolu olan TUM
    hayvanlar, guncel durumlari ne olursa olsun. Baba kimligi sire_id ile
    birlikte hem kupe no (suruye aitse) hem soy kutugu kayit no (girilmisse)
    olarak dondurulur - gosterim onceligi frontend'de belirlenir (bkz.
    OffspringBySireRead). Boga adina, sonra dogum tarihine gore siralanir."""
    stmt = (
        select(Animal)
        .join(Sire, Animal.father_sire_id == Sire.id)
        .options(
            joinedload(Animal.father_sire).joinedload(Sire.animal),
            joinedload(Animal.mother),
            joinedload(Animal.gender),
            joinedload(Animal.status),
        )
        .where(Animal.father_sire_id.isnot(None), Animal.birth_date.isnot(None))
        .order_by(Sire.name, Animal.birth_date)
    )
    rows: list[OffspringBySireRead] = []
    for animal in db.scalars(stmt).all():
        sire = animal.father_sire
        assert sire is not None and animal.birth_date is not None
        rows.append(
            OffspringBySireRead(
                sire_id=sire.id,
                sire_tag_number=sire.animal.tag_number if sire.animal else None,
                sire_registry_no=sire.registry_no,
                sire_name=sire.name,
                animal_id=animal.id,
                tag_number=animal.tag_number,
                name=animal.name,
                birth_date=animal.birth_date,
                gender_name=animal.gender.name,
                mother_tag_number=animal.mother.tag_number if animal.mother else None,
                status_name=animal.status.name,
            )
        )
    return rows


def list_calving_intervals(db: Session) -> list[CalvingIntervalRead]:
    """Her inek icin gecmisteki TUM dogumlarini (Animal.mother_id + birth_date)
    tarihe gore siralayip son iki dogum arasindaki gun farkini (yavrulama
    araligi) hesaplar. Tarih araligi gerektirmez - sureklilik gosteren, yavas
    degisen bir verimlilik gostergesidir (Anayasa m.4/m.5: hicbir yerde
    saklanmaz, her istek Animal.birth_date/mother_id'den turetilir).

    Ayni tarihte dogan yavrular (ikiz/ucuz) TEK yavrulama olayi sayilir -
    aksi halde ikiz dogumlar aralarinda 0 gun fark varmis gibi ayri birer
    "dogum" olarak sayilip yavrulama araligini yapay olarak dusurur."""
    stmt = (
        select(Animal.mother_id, Animal.birth_date)
        .where(Animal.mother_id.isnot(None), Animal.birth_date.isnot(None))
        .order_by(Animal.mother_id, Animal.birth_date)
    )
    calving_dates_by_dam: dict[uuid.UUID, set[date]] = {}
    for mother_id, birth_date in db.execute(stmt).all():
        calving_dates_by_dam.setdefault(mother_id, set()).add(birth_date)

    dam_ids = list(calving_dates_by_dam.keys())
    dams = {a.id: a for a in db.scalars(select(Animal).where(Animal.id.in_(dam_ids))).all()} if dam_ids else {}

    dam_rows: list[CalvingIntervalRead] = []
    for dam_id, date_set in calving_dates_by_dam.items():
        dates = sorted(date_set)
        if len(dates) < 2:
            continue
        previous_calving, last_calving = dates[-2], dates[-1]
        interval_days = (last_calving - previous_calving).days
        dam = dams.get(dam_id)
        dam_rows.append(
            CalvingIntervalRead(
                animal_id=dam_id,
                tag_number=dam.tag_number if dam else "—",
                name=dam.name if dam else None,
                previous_calving_date=previous_calving,
                last_calving_date=last_calving,
                interval_days=interval_days,
                calving_count=len(dates),
            )
        )
    dam_rows.sort(key=lambda r: -r.interval_days)

    if not dam_rows:
        return []

    average_interval = round(sum(r.interval_days for r in dam_rows) / len(dam_rows))
    summary_row = CalvingIntervalRead(
        is_summary=True,
        tag_number="Sürü Ortalaması",
        interval_days=average_interval,
        calving_count=len(dam_rows),
    )
    return [summary_row, *dam_rows]


@dataclass
class _PerformanceBucket:
    source_type: str
    source_label: str
    service_count: int = 0
    pregnant_count: int = 0
    open_count: int = 0
    suspicious_count: int = 0
    pending_count: int = 0


def list_breeding_performance(db: Session, start_date: date, end_date: date) -> list[BreedingPerformanceRead]:
    """Belirtilen tarih araliginda yapilan asimlar; boga (dogal asim) ya da
    sperma partisi (suni tohumlama/embriyo) bazinda gebe kalma orani."""
    stmt = (
        select(BreedingEvent)
        .options(
            joinedload(BreedingEvent.service_method),
            joinedload(BreedingEvent.sire_animal),
            joinedload(BreedingEvent.semen_batch).joinedload(SemenBatch.sire),
        )
        .where(BreedingEvent.service_date >= start_date, BreedingEvent.service_date <= end_date)
    )
    events = list(db.scalars(stmt).all())
    latest_checks = _latest_check_by_event(db)

    buckets: dict[str, _PerformanceBucket] = {}
    for event in events:
        if event.sire_animal_id is not None:
            key = f"sire:{event.sire_animal_id}"
            sire_animal = event.sire_animal
            label = f"{sire_animal.tag_number}{' - ' + sire_animal.name if sire_animal.name else ''}"
        else:
            assert event.semen_batch_id is not None
            key = f"batch:{event.semen_batch_id}"
            batch = event.semen_batch
            label = f"{batch.batch_no} ({batch.sire.name})"

        bucket = buckets.get(key)
        if bucket is None:
            bucket = _PerformanceBucket(source_type=event.service_method.name, source_label=label)
            buckets[key] = bucket

        bucket.service_count += 1
        check = latest_checks.get(event.id)
        if check is None:
            bucket.pending_count += 1
        elif check.result.code == "GEBE":
            bucket.pregnant_count += 1
        elif check.result.code == "BOS":
            bucket.open_count += 1
        else:
            bucket.suspicious_count += 1

    rows: list[BreedingPerformanceRead] = []
    for bucket in buckets.values():
        checked_total = bucket.pregnant_count + bucket.open_count
        rate = round(bucket.pregnant_count / checked_total * 100, 1) if checked_total > 0 else None
        rows.append(
            BreedingPerformanceRead(
                source_type=bucket.source_type,
                source_label=bucket.source_label,
                service_count=bucket.service_count,
                pregnant_count=bucket.pregnant_count,
                open_count=bucket.open_count,
                suspicious_count=bucket.suspicious_count,
                pending_count=bucket.pending_count,
                pregnancy_rate=rate,
            )
        )
    rows.sort(key=lambda r: (r.pregnancy_rate is None, -(r.pregnancy_rate or 0), -r.service_count))
    return rows


def list_pregnancy_check_results(db: Session, start_date: date, end_date: date) -> list[PregnancyCheckResultRead]:
    """Belirtilen tarih araliginda (check_date) yapilan tum gebelik kontrolleri -
    hangi hayvana, hangi yontemle, ne sonuc cikti."""
    stmt = (
        select(PregnancyCheck)
        .options(
            joinedload(PregnancyCheck.method),
            joinedload(PregnancyCheck.result),
            joinedload(PregnancyCheck.breeding_event).joinedload(BreedingEvent.dam),
        )
        .where(PregnancyCheck.check_date >= start_date, PregnancyCheck.check_date <= end_date)
        .order_by(PregnancyCheck.check_date, PregnancyCheck.breeding_event_id)
    )
    rows: list[PregnancyCheckResultRead] = []
    for check in db.scalars(stmt).all():
        event = check.breeding_event
        dam = event.dam
        rows.append(
            PregnancyCheckResultRead(
                breeding_event_id=event.id,
                animal_id=dam.id,
                tag_number=dam.tag_number,
                name=dam.name,
                service_date=event.service_date,
                check_date=check.check_date,
                method_name=check.method.name,
                result_name=check.result.name,
                is_suspicious=check.result.code == "SUPHELI",
                note=check.note,
            )
        )
    return rows


def list_health_events(db: Session, start_date: date, end_date: date) -> list[HealthEventReportRead]:
    """Belirtilen tarih araliginda (event_date) kaydedilen tum saglik olaylari -
    hastalik dagilimi ve ilac kullanim sikligi bu listeden turetilir."""
    stmt = (
        select(HealthEvent)
        .options(
            joinedload(HealthEvent.animal),
            joinedload(HealthEvent.event_type),
            joinedload(HealthEvent.disease),
            joinedload(HealthEvent.medication),
            joinedload(HealthEvent.dosage_unit),
        )
        .where(HealthEvent.event_date >= start_date, HealthEvent.event_date <= end_date)
        .order_by(HealthEvent.event_date, HealthEvent.animal_id)
    )
    rows: list[HealthEventReportRead] = []
    for event in db.scalars(stmt).all():
        rows.append(
            HealthEventReportRead(
                animal_id=event.animal_id,
                tag_number=event.animal.tag_number,
                name=event.animal.name,
                event_date=event.event_date,
                event_type_name=event.event_type.name,
                is_illness=event.event_type.code == ILLNESS_EVENT_TYPE_CODE or event.disease_id is not None,
                disease_name=event.disease.name if event.disease else None,
                medication_name=event.medication.name if event.medication else None,
                dosage_amount=event.dosage_amount,
                dosage_unit_name=event.dosage_unit.name if event.dosage_unit else None,
                veterinarian_note=event.veterinarian_note,
            )
        )
    return rows


def list_weight_gains(db: Session, start_date: date, end_date: date) -> list[WeightGainRead]:
    """Belirtilen tarih araliginda en az iki tartisi olan hayvanlar icin, aralikta
    ilk ve son tarti arasindaki gunluk ortalama canli agirlik artisini (ADG)
    hesaplar. Anayasa m.5: ADG hicbir yerde saklanmaz, iki weight_records
    kaydindan burada turetilir."""
    stmt = (
        select(WeightRecord)
        .options(joinedload(WeightRecord.animal))
        .where(WeightRecord.weigh_date >= start_date, WeightRecord.weigh_date <= end_date)
        .order_by(WeightRecord.animal_id, WeightRecord.weigh_date)
    )
    by_animal: dict[uuid.UUID, list[WeightRecord]] = {}
    for record in db.scalars(stmt).all():
        by_animal.setdefault(record.animal_id, []).append(record)

    rows: list[WeightGainRead] = []
    for records in by_animal.values():
        if len(records) < 2:
            continue
        first, last = records[0], records[-1]
        days = (last.weigh_date - first.weigh_date).days
        if days <= 0:
            continue
        gain = last.weight_kg - first.weight_kg
        rows.append(
            WeightGainRead(
                animal_id=first.animal_id,
                tag_number=first.animal.tag_number,
                name=first.animal.name,
                first_weigh_date=first.weigh_date,
                first_weight_kg=first.weight_kg,
                last_weigh_date=last.weigh_date,
                last_weight_kg=last.weight_kg,
                days_between=days,
                weight_gain_kg=gain,
                average_daily_gain_kg=round(float(gain) / days, 3),
                note=last.note,
            )
        )
    rows.sort(key=lambda r: r.average_daily_gain_kg)
    return rows


@dataclass
class _SalesBucket:
    buyer_name: str
    sale_count: int = 0
    total_weight_kg: Decimal = field(default_factory=lambda: Decimal("0"))
    total_revenue: Decimal = field(default_factory=lambda: Decimal("0"))


def list_sales_report(db: Session, start_date: date, end_date: date) -> list[SalesReportRead]:
    """Belirtilen tarih araliginda (sale_date) yapilan satislar, alici bazinda
    gruplanip toplam gelir, toplam agirlik ve ortalama fiyatlarla ozetlenir."""
    stmt = (
        select(Sale)
        .options(joinedload(Sale.buyer))
        .where(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
    )
    buckets: dict[int, _SalesBucket] = {}
    for sale in db.scalars(stmt).all():
        bucket = buckets.get(sale.buyer_id)
        if bucket is None:
            bucket = _SalesBucket(buyer_name=sale.buyer.name)
            buckets[sale.buyer_id] = bucket
        bucket.sale_count += 1
        bucket.total_revenue += sale.total_amount
        if sale.sale_weight_kg:
            bucket.total_weight_kg += sale.sale_weight_kg

    rows: list[SalesReportRead] = []
    for bucket in buckets.values():
        rows.append(
            SalesReportRead(
                buyer_name=bucket.buyer_name,
                sale_count=bucket.sale_count,
                total_weight_kg=bucket.total_weight_kg,
                total_revenue=bucket.total_revenue,
                average_sale_amount=round(float(bucket.total_revenue) / bucket.sale_count, 2),
                average_price_per_kg=(
                    round(float(bucket.total_revenue) / float(bucket.total_weight_kg), 2)
                    if bucket.total_weight_kg > 0
                    else None
                ),
            )
        )
    rows.sort(key=lambda r: -r.total_revenue)
    return rows


@dataclass
class _FeedBucket:
    pen_code: str
    pen_name: str
    feed_item_name: str
    feed_type_name: str
    total_quantity_kg: float = 0.0
    active_days: int = 0


def _rations_overlapping(db: Session, start_date: date, end_date: date) -> list[PenRation]:
    stmt = (
        select(PenRation)
        .options(
            joinedload(PenRation.pen),
            joinedload(PenRation.items).joinedload(RationItem.feed_item).joinedload(FeedItem.feed_type),
            joinedload(PenRation.items).joinedload(RationItem.unit),
        )
        .where(PenRation.start_date <= end_date, (PenRation.end_date.is_(None)) | (PenRation.end_date >= start_date))
    )
    return list(db.scalars(stmt).unique().all())


def list_feed_consumption(db: Session, start_date: date, end_date: date) -> list[FeedConsumptionRead]:
    """[start_date, end_date] ile kesisen rasyon donemlerinden, padok + yem
    urunu bazinda toplam tuketimi turetir - gunluk dagitim kaydi YOKTUR
    (bkz. app/modules/feed/models.py). Miktar, o gunku FIILI hayvan
    sayisiyla (pen_assignments) carpilarak hesaplanir, hicbir yerde
    saklanmaz (Anayasa m.4/m.5)."""
    rations = _rations_overlapping(db, start_date, end_date)
    if not rations:
        return []

    assignments_by_pen: dict[int, list[PenAssignment]] = {}
    for pen_id in {r.pen_id for r in rations}:
        assignments_by_pen[pen_id] = list(
            db.scalars(select(PenAssignment).where(PenAssignment.pen_id == pen_id)).all()
        )

    buckets: dict[tuple[int, int], _FeedBucket] = {}
    for ration in rations:
        overlap_start = max(ration.start_date, start_date)
        overlap_end = min(ration.end_date or end_date, end_date)
        if overlap_start > overlap_end:
            continue
        headcounts = _daily_headcounts(assignments_by_pen[ration.pen_id], overlap_start, overlap_end)
        active_days = sum(1 for count in headcounts.values() if count > 0)
        for item in ration.items:
            key = (ration.pen_id, item.feed_item_id)
            bucket = buckets.get(key)
            if bucket is None:
                bucket = _FeedBucket(
                    pen_code=ration.pen.code,
                    pen_name=ration.pen.name,
                    feed_item_name=item.feed_item.name,
                    feed_type_name=item.feed_item.feed_type.name,
                )
                buckets[key] = bucket
            per_animal_kg = _to_kg(item.daily_quantity_per_animal, item.unit.code)
            bucket.total_quantity_kg += sum(per_animal_kg * count for count in headcounts.values())
            bucket.active_days += active_days

    rows = [
        FeedConsumptionRead(
            pen_code=b.pen_code,
            pen_name=b.pen_name,
            feed_item_name=b.feed_item_name,
            feed_type_name=b.feed_type_name,
            total_quantity_kg=round(b.total_quantity_kg, 2),
            active_days=b.active_days,
        )
        for b in buckets.values()
    ]
    rows.sort(key=lambda r: -r.total_quantity_kg)
    return rows


def list_feed_stock_status(db: Session, as_of_date: date | None = None) -> list[FeedStockStatusRead]:
    """Her yem urunu icin: toplam alim - toplam tuketim (TUM rasyon
    donemlerinden turetilir) = mevcut stok. Agirlikli ortalama birim
    maliyetle (bkz. _feed_avg_cost_per_kg) carpilarak stok degeri (TL) de
    hesaplanir - hicbiri saklanmaz (Anayasa m.5)."""
    as_of_date = as_of_date or date.today()
    rows: list[FeedStockStatusRead] = []

    for feed_item in db.scalars(
        select(FeedItem).options(joinedload(FeedItem.feed_type)).order_by(FeedItem.name)
    ).all():
        purchases = db.scalars(
            select(FeedPurchase)
            .options(joinedload(FeedPurchase.unit))
            .where(FeedPurchase.feed_item_id == feed_item.id, FeedPurchase.purchase_date <= as_of_date)
        ).all()
        total_purchased_kg = sum(_to_kg(p.quantity, p.unit.code) for p in purchases)

        ration_items = db.scalars(
            select(RationItem)
            .join(PenRation)
            .options(
                joinedload(RationItem.unit),
                joinedload(RationItem.ration),
            )
            .where(RationItem.feed_item_id == feed_item.id, PenRation.start_date <= as_of_date)
        ).unique().all()

        total_consumed_kg = 0.0
        pens_seen: dict[int, list[PenAssignment]] = {}
        for item in ration_items:
            ration = item.ration
            overlap_end = min(ration.end_date or as_of_date, as_of_date)
            if ration.start_date > overlap_end:
                continue
            if ration.pen_id not in pens_seen:
                pens_seen[ration.pen_id] = list(
                    db.scalars(select(PenAssignment).where(PenAssignment.pen_id == ration.pen_id)).all()
                )
            headcounts = _daily_headcounts(pens_seen[ration.pen_id], ration.start_date, overlap_end)
            per_animal_kg = _to_kg(item.daily_quantity_per_animal, item.unit.code)
            total_consumed_kg += sum(per_animal_kg * count for count in headcounts.values())

        if total_purchased_kg == 0 and total_consumed_kg == 0:
            continue

        stock_kg = total_purchased_kg - total_consumed_kg
        avg_cost = _feed_avg_cost_per_kg(db, feed_item.id, as_of_date)
        stock_value_try = (Decimal(str(stock_kg)) * avg_cost) if avg_cost is not None else None

        rows.append(
            FeedStockStatusRead(
                feed_item_name=feed_item.name,
                feed_type_name=feed_item.feed_type.name,
                total_purchased_kg=round(total_purchased_kg, 2),
                total_consumed_kg=round(total_consumed_kg, 2),
                stock_kg=round(stock_kg, 2),
                avg_cost_per_kg_try=round(float(avg_cost), 2) if avg_cost is not None else None,
                stock_value_try=_round_money(stock_value_try) if stock_value_try is not None else None,
            )
        )
    rows.sort(key=lambda r: r.feed_item_name)
    return rows


def list_herd_flow(db: Session, start_date: date, end_date: date) -> list[HerdFlowReportRead]:
    """Belirtilen tarih araliginda surunun giris (entry_date, kaynagina gore
    kirilim) ve cikis (satis + olum) hareketlerini ozetler, net degisimi
    hesaplar. Anayasa m.4/m.5: hicbir "hareket" tablosu yok, uc ayri modulun
    (Animal.entry_date, Sale, Death) tarih alanlarindan burada turetilir."""
    entry_stmt = (
        select(EntrySource.name, func.count(Animal.id))
        .join(EntrySource, Animal.entry_source_id == EntrySource.id)
        .where(Animal.entry_date >= start_date, Animal.entry_date <= end_date)
        .group_by(EntrySource.name)
    )
    entry_counts = db.execute(entry_stmt).all()

    sale_count = db.scalar(
        select(func.count()).select_from(Sale).where(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
    ) or 0
    death_count = db.scalar(
        select(func.count()).select_from(Death).where(Death.death_date >= start_date, Death.death_date <= end_date)
    ) or 0

    rows: list[HerdFlowReportRead] = []
    total_in = 0
    for name, count in entry_counts:
        rows.append(HerdFlowReportRead(category=f"Giriş - {name}", direction="Giriş", direction_code="IN", count=count))
        total_in += count

    rows.append(HerdFlowReportRead(category="Çıkış - Satış", direction="Çıkış", direction_code="OUT", count=sale_count))
    rows.append(HerdFlowReportRead(category="Çıkış - Ölüm", direction="Çıkış", direction_code="OUT", count=death_count))
    total_out = sale_count + death_count

    rows.append(
        HerdFlowReportRead(category="Net Değişim", direction="Net", direction_code="NET", count=total_in - total_out)
    )
    return rows


def _death_age_group(animal: Animal, at_date: date) -> str:
    if animal.birth_date is None:
        return "Yetişkin (7+ Ay)"
    age_months = full_months_between(animal.birth_date, at_date)
    return "Buzağı (0-7 Ay)" if age_months < CALF_MAX_MONTHS else "Yetişkin (7+ Ay)"


def list_death_losses(db: Session, start_date: date, end_date: date, today: date | None = None) -> list[DeathLossReportRead]:
    """Belirtilen tarih araliginda (death_date) olen hayvanlari, olum aninda ki
    yasina gore buzagi/yetiskin diye ikiye ayirip neden dagilimi ve kayip
    oranini (o kategorideki mevcut aktif hayvan sayisina oranla) hesaplar."""
    today = today or date.today()
    stmt = (
        select(Death)
        .options(joinedload(Death.animal), joinedload(Death.death_reason))
        .where(Death.death_date >= start_date, Death.death_date <= end_date)
    )
    groups = ("Buzağı (0-7 Ay)", "Yetişkin (7+ Ay)")
    death_counts: dict[str, int] = {g: 0 for g in groups}
    reason_counts: dict[str, dict[str, int]] = {g: {} for g in groups}
    for death in db.scalars(stmt).all():
        group = _death_age_group(death.animal, death.death_date)
        death_counts[group] += 1
        reason_name = death.death_reason.name
        reason_counts[group][reason_name] = reason_counts[group].get(reason_name, 0) + 1

    active_counts: dict[str, int] = {g: 0 for g in groups}
    for animal, age_months in _active_animals_with_age(db, today):
        key = "Buzağı (0-7 Ay)" if age_months < CALF_MAX_MONTHS else "Yetişkin (7+ Ay)"
        active_counts[key] += 1

    rows: list[DeathLossReportRead] = []
    for group in groups:
        dcount = death_counts[group]
        acount = active_counts[group]
        breakdown = ", ".join(
            f"{name} ({count})" for name, count in sorted(reason_counts[group].items(), key=lambda kv: -kv[1])
        )
        rate = round(dcount / (dcount + acount) * 100, 1) if (dcount + acount) > 0 else None
        rows.append(
            DeathLossReportRead(
                age_group=group,
                death_count=dcount,
                reason_breakdown=breakdown,
                current_active_count=acount,
                loss_rate=rate,
            )
        )

    # Iki grubun BIRLESIK toplami - dashboard'daki "Yillik Kayip Orani"
    # tek bir suru-geneli oran verdigi icin (bkz. get_dashboard_summary),
    # buradaki ayri buzagi/yetiskin satirlarindan dogrudan karsilastirma
    # yapilamiyordu. Bu satir aynı hesabi (toplam olum / toplam olum+aktif)
    # burada da gosterip iki rakamin neden farkli oldugunu gorunur kilar.
    total_dcount = sum(death_counts.values())
    total_acount = sum(active_counts.values())
    total_reason_counts: dict[str, int] = {}
    for group_reasons in reason_counts.values():
        for name, count in group_reasons.items():
            total_reason_counts[name] = total_reason_counts.get(name, 0) + count
    total_breakdown = ", ".join(
        f"{name} ({count})" for name, count in sorted(total_reason_counts.items(), key=lambda kv: -kv[1])
    )
    total_rate = round(total_dcount / (total_dcount + total_acount) * 100, 1) if (total_dcount + total_acount) > 0 else None
    rows.append(
        DeathLossReportRead(
            age_group="Toplam",
            death_count=total_dcount,
            reason_breakdown=total_breakdown,
            current_active_count=total_acount,
            loss_rate=total_rate,
            is_summary=True,
        )
    )
    return rows


def _active_animals_with_age(db: Session, today: date) -> list[tuple[Animal, int]]:
    active_id = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE).id
    stmt = (
        select(Animal)
        .options(
            joinedload(Animal.gender),
            joinedload(Animal.mother),
            joinedload(Animal.father_sire),
            joinedload(Animal.breed),
        )
        .where(Animal.status_id == active_id, Animal.birth_date.isnot(None))
        .order_by(Animal.birth_date)
    )
    return [(a, full_months_between(a.birth_date, today)) for a in db.scalars(stmt).all()]


def list_animals_by_status(db: Session, status_ids: list[int] | None = None, today: date | None = None) -> list[YoungAnimalRead]:
    """Hayvanlari (istege bagli) durum (AnimalStatus) filtresine gore
    listeler - status_ids bos/None ise HERHANGI BIR durumdaki tum
    hayvanlar doner (calves/heifers-steers'in aksine yas araligina gore
    filtrelemez). Yas gibi turetilmis alanlar (bkz. full_months_between)
    hicbir yerde saklanmaz, yalnizca burada hesaplanir."""
    today = today or date.today()
    stmt = (
        select(Animal)
        .options(
            joinedload(Animal.gender),
            joinedload(Animal.mother),
            joinedload(Animal.father_sire),
            joinedload(Animal.breed),
        )
        .order_by(Animal.birth_date, Animal.tag_number)
    )
    if status_ids:
        stmt = stmt.where(Animal.status_id.in_(status_ids))
    rows: list[YoungAnimalRead] = []
    for animal in db.scalars(stmt).all():
        age_months = full_months_between(animal.birth_date, today) if animal.birth_date else None
        rows.append(
            YoungAnimalRead(
                animal_id=animal.id,
                tag_number=animal.tag_number,
                name=animal.name,
                gender_name=animal.gender.name,
                breed_name=animal.breed.name if animal.breed else None,
                birth_date=animal.birth_date,
                age_months=age_months,
                age_days=(today - animal.birth_date).days if animal.birth_date else None,
                mother_tag_number=animal.mother.tag_number if animal.mother else None,
                father_sire_name=animal.father_sire.name if animal.father_sire else None,
                note=animal.note,
            )
        )
    return rows


def list_calves(db: Session, today: date | None = None) -> list[YoungAnimalRead]:
    today = today or date.today()
    rows: list[YoungAnimalRead] = []
    for animal, age_months in _active_animals_with_age(db, today):
        if not (0 <= age_months < CALF_MAX_MONTHS):
            continue
        rows.append(_to_young_animal_read(animal, age_months, today))
    return rows


def list_heifers_and_steers(db: Session, today: date | None = None) -> list[YoungAnimalRead]:
    today = today or date.today()
    rows: list[YoungAnimalRead] = []
    for animal, age_months in _active_animals_with_age(db, today):
        if not (CALF_MAX_MONTHS <= age_months < BREEDING_AGE_MONTHS):
            continue
        rows.append(_to_young_animal_read(animal, age_months, today))
    return rows


def _to_young_animal_read(animal: Animal, age_months: int, today: date) -> YoungAnimalRead:
    return YoungAnimalRead(
        animal_id=animal.id,
        tag_number=animal.tag_number,
        name=animal.name,
        gender_name=animal.gender.name,
        breed_name=animal.breed.name if animal.breed else None,
        birth_date=animal.birth_date,
        age_months=age_months,
        age_days=(today - animal.birth_date).days if animal.birth_date else None,
        mother_tag_number=animal.mother.tag_number if animal.mother else None,
        father_sire_name=animal.father_sire.name if animal.father_sire else None,
        note=animal.note,
    )


def list_pen_occupancy(db: Session) -> list[PenOccupancyRead]:
    counts_stmt = (
        select(PenAssignment.pen_id, func.count(PenAssignment.id))
        .where(PenAssignment.removed_date.is_(None))
        .group_by(PenAssignment.pen_id)
    )
    counts = dict(db.execute(counts_stmt).all())
    rows: list[PenOccupancyRead] = []
    for pen in db.scalars(select(Pen).order_by(Pen.code)).all():
        current_count = counts.get(pen.id, 0)
        occupancy_rate = round(current_count / pen.capacity * 100, 1) if pen.capacity else None
        rows.append(
            PenOccupancyRead(
                pen_id=pen.id,
                code=pen.code,
                name=pen.name,
                capacity=pen.capacity,
                current_count=current_count,
                occupancy_rate=occupancy_rate,
            )
        )
    return rows


def get_herd_inventory(db: Session, today: date | None = None) -> HerdInventoryRead:
    today = today or date.today()
    female_id = get_lookup_by_code(db, Gender, FEMALE_GENDER_CODE).id
    male_id = get_lookup_by_code(db, Gender, MALE_GENDER_CODE).id
    active_id = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE).id

    status_counts_stmt = (
        select(AnimalStatus.code, func.count(Animal.id))
        .join(AnimalStatus, Animal.status_id == AnimalStatus.id)
        .group_by(AnimalStatus.code)
    )
    by_status = dict(db.execute(status_counts_stmt).all())

    gender_counts_stmt = (
        select(Animal.gender_id, func.count(Animal.id)).where(Animal.status_id == active_id).group_by(Animal.gender_id)
    )
    gender_counts = dict(db.execute(gender_counts_stmt).all())

    # Yas kovalarina (buzagi/duve-dana/yetiskin) sadece dogum tarihi girilmis
    # aktif hayvanlar dahil olur - satin alinip dogum tarihi bilinmeyen
    # hayvanlar bu kovalara giremez ama genel cinsiyet toplamlarina girer.
    active_with_age = _active_animals_with_age(db, today)
    calves_count = sum(1 for _, m in active_with_age if 0 <= m < CALF_MAX_MONTHS)
    heifers_steers_count = sum(1 for _, m in active_with_age if CALF_MAX_MONTHS <= m < BREEDING_AGE_MONTHS)
    breeding_age_female_count = sum(1 for a, m in active_with_age if a.gender_id == female_id and m >= BREEDING_AGE_MONTHS)
    adult_male_count = sum(1 for a, m in active_with_age if a.gender_id == male_id and m >= BREEDING_AGE_MONTHS)

    return HerdInventoryRead(
        total_active=by_status.get(ACTIVE_STATUS_CODE, 0),
        by_status=by_status,
        female_active=gender_counts.get(female_id, 0),
        male_active=gender_counts.get(male_id, 0),
        calves_count=calves_count,
        heifers_steers_count=heifers_steers_count,
        breeding_age_female_count=breeding_age_female_count,
        adult_male_count=adult_male_count,
    )


def list_herd_status_summary(db: Session, today: date | None = None) -> list[HerdStatusSummaryRead]:
    """Surunun guncel durumunun tek tabloda ozeti - Aktif Hayvanlar
    raporundaki yas kovalarini (Buzagi/Duve-Tosun/Yetiskin Erkek) ile
    Tohumlanacak Hayvanlar + Tohumlu ve Gebe Hayvanlar raporlarindaki
    ureme alt-durumlarini BIRLESTIRIR.

    "Dogurgan Yasta Disi" ara toplami, altindaki 7 ureme alt-durumunun
    toplamina TAM OLARAK esittir: her aktif disi _classify_female'de bu 7
    durumdan (candidate_new, postpartum_waiting, candidate_postpartum,
    open, pending, suspicious, pregnant) birine ya da "none"a duser;
    "none" sadece 12 aydan kucuk ya da dogum tarihi bilinmeyen disilerde
    olusur ve zaten dogurgan yas kovasina hic girmez (bkz. dosya basi
    docstring, get_herd_inventory). Yeni bir hesap eklemez, sadece
    get_herd_inventory + list_breeding_candidates + list_bred_animals
    sonuclarini yeniden duzenler.
    """
    today = today or date.today()
    inventory = get_herd_inventory(db, today)
    candidates = list_breeding_candidates(db, today)
    bred = list_bred_animals(db, today)

    candidate_counts = {"candidate_new": 0, "postpartum_waiting": 0, "candidate_postpartum": 0, "open": 0}
    for c in candidates:
        if c.reason_code in candidate_counts:
            candidate_counts[c.reason_code] += 1

    bred_counts = {"Tohumlu": 0, "Şüpheli": 0, "Gebe": 0}
    for b in bred:
        if b.check_status in bred_counts:
            bred_counts[b.check_status] += 1

    return [
        HerdStatusSummaryRead(category="Buzağı", count=inventory.calves_count),
        HerdStatusSummaryRead(category="Düve/Tosun", count=inventory.heifers_steers_count),
        HerdStatusSummaryRead(
            category="Doğurgan Yaştaki Dişi (Toplam)", count=inventory.breeding_age_female_count, is_total=True
        ),
        HerdStatusSummaryRead(
            category="Tohumlanacak (İlk Tohumlama)", count=candidate_counts["candidate_new"], level=1
        ),
        HerdStatusSummaryRead(
            category="Post Partum (Bekliyor)", count=candidate_counts["postpartum_waiting"], level=1
        ),
        HerdStatusSummaryRead(
            category="Tohumlanacak (Doğum Sonrası)", count=candidate_counts["candidate_postpartum"], level=1
        ),
        HerdStatusSummaryRead(category="Tekrar Kızgınlık / Boş", count=candidate_counts["open"], level=1),
        HerdStatusSummaryRead(category="Tohumlu (Kontrol Bekliyor)", count=bred_counts["Tohumlu"], level=1),
        HerdStatusSummaryRead(
            category="Şüpheli (Tekrar Kontrol Gerekli)", count=bred_counts["Şüpheli"], level=1
        ),
        HerdStatusSummaryRead(category="Gebe", count=bred_counts["Gebe"], level=1),
        HerdStatusSummaryRead(category="Yetişkin Erkek", count=inventory.adult_male_count),
        HerdStatusSummaryRead(category="Toplam Aktif", count=inventory.total_active, is_total=True),
    ]


def get_dashboard_summary(db: Session, today: date | None = None) -> DashboardSummaryRead:
    today = today or date.today()
    inventory = get_herd_inventory(db, today)
    bred_animals = list_bred_animals(db, today)
    pen_occupancy = list_pen_occupancy(db)

    capacities = [p for p in pen_occupancy if p.capacity]
    pen_occupancy_rate = (
        round(sum(p.current_count for p in capacities) / sum(p.capacity for p in capacities) * 100, 1)
        if capacities
        else None
    )

    calving_intervals = list_calving_intervals(db)
    average_calving_interval = calving_intervals[0].interval_days if calving_intervals else None

    # is_summary=True satiri (Toplam) zaten buzagi+yetiskin toplami oldugu
    # icin disarida birakiliyor - yoksa cift sayim olurdu.
    yearly_losses = [r for r in list_death_losses(db, today - timedelta(days=365), today, today) if not r.is_summary]
    total_deaths = sum(r.death_count for r in yearly_losses)
    total_active_for_loss = sum(r.current_active_count for r in yearly_losses)
    annual_loss_rate = (
        round(total_deaths / (total_deaths + total_active_for_loss) * 100, 1)
        if (total_deaths + total_active_for_loss) > 0
        else None
    )

    breeding_candidates = list_breeding_candidates(db, today)

    return DashboardSummaryRead(
        active_animal_count=inventory.total_active,
        # "Post Partum" (henuz dogum sonrasi bekleme suresini tamamlamamis,
        # bilgi amacli) haric - bu sayac SADECE gercekten aksiyon gerektiren
        # (tohumlanmaya hazir) hayvanlari yansitir.
        breeding_candidate_count=sum(1 for c in breeding_candidates if c.reason_code != "postpartum_waiting"),
        pregnancy_check_due_count=sum(1 for b in bred_animals if b.pregnancy_check_due),
        pregnant_count=sum(1 for b in bred_animals if b.check_status == "Gebe"),
        repeat_breeder_count=sum(1 for c in breeding_candidates if c.reason == "Tekrar Kızgınlık / Boş"),
        calves_count=inventory.calves_count,
        heifers_steers_count=inventory.heifers_steers_count,
        pen_occupancy_rate=pen_occupancy_rate,
        average_calving_interval_days=average_calving_interval,
        annual_loss_rate=annual_loss_rate,
    )


# --- Maliyet / Verimlilik / Kârlılık ---
#
# Bu bolumdeki raporlar, TL tutarlarin yaninda TCMB'nin gunluk kur XML
# servisinden (bkz. app/modules/fx) turetilen USD karsiliklarini da
# dondurur. Her TL tutari KENDI GERCEK TARIHINDEKI kurla cevrilir (bugunun
# kuruyla degil) - boylece tarihsel maliyet hic degistirilmeden, yuksek TL
# enflasyonuna ragmen donemler arasi karsilastirilabilir hale gelir. Kur
# bulunamazsa (ag hatasi) o kalem USD toplamina 0 katkida bulunur - rapor
# yine de TL rakamlariyla eksiksiz kalir (Anayasa m.4/m.5: hicbir USD
# degeri saklanmaz, her istek burada yeniden hesaplanir).

_MONEY_QUANTIZE = Decimal("0.01")


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(_MONEY_QUANTIZE)


def _try_to_usd(db: Session, try_amount: Decimal, on_date: date) -> Decimal:
    if try_amount == 0:
        return Decimal("0")
    rate = fx_service.get_usd_try_rate(db, on_date)
    if not rate:
        return Decimal("0")
    return try_amount / rate


@dataclass
class _PenEfficiencyBucket:
    code: str
    name: str
    total_feed_quantity_kg: float = 0.0
    total_feed_cost_try: Decimal = field(default_factory=lambda: Decimal("0"))
    total_feed_cost_usd: Decimal = field(default_factory=lambda: Decimal("0"))
    total_weight_gain_kg: Decimal = field(default_factory=lambda: Decimal("0"))


def list_pen_efficiency(db: Session, start_date: date, end_date: date) -> list[PenEfficiencyRead]:
    """Padok bazinda yem donusum orani (FCR) ve kg canli agirlik basina
    maliyet. Toplam yem (miktar + maliyet, TL/USD), [start_date, end_date]
    ile kesisen rasyon donemlerinden (bkz. list_feed_consumption ile ayni
    turetme mantigi); toplam kilo artisi ise pen_assignments araliklariyla
    KESISEN weight_records ciftlerinden (ilk/son tarti farki) turetilir -
    bir hayvan donem icinde padok degistirse bile kilosu dogru padoga
    yazilir (Anayasa m.4/m.5: hicbir yerde saklanmaz)."""
    buckets: dict[int, _PenEfficiencyBucket] = {}

    rations = _rations_overlapping(db, start_date, end_date)
    assignments_by_pen: dict[int, list[PenAssignment]] = {}
    for pen_id in {r.pen_id for r in rations}:
        assignments_by_pen[pen_id] = list(
            db.scalars(select(PenAssignment).where(PenAssignment.pen_id == pen_id)).all()
        )

    for ration in rations:
        overlap_start = max(ration.start_date, start_date)
        overlap_end = min(ration.end_date or end_date, end_date)
        if overlap_start > overlap_end:
            continue
        headcounts = _daily_headcounts(assignments_by_pen[ration.pen_id], overlap_start, overlap_end)
        bucket = buckets.get(ration.pen_id)
        if bucket is None:
            bucket = _PenEfficiencyBucket(code=ration.pen.code, name=ration.pen.name)
            buckets[ration.pen_id] = bucket
        for item in ration.items:
            per_animal_kg = _to_kg(item.daily_quantity_per_animal, item.unit.code)
            total_kg = sum(per_animal_kg * count for count in headcounts.values())
            bucket.total_feed_quantity_kg += total_kg
            avg_cost = _feed_avg_cost_per_kg(db, item.feed_item_id, end_date)
            if avg_cost is not None:
                cost_try = Decimal(str(total_kg)) * avg_cost
                bucket.total_feed_cost_try += cost_try
                bucket.total_feed_cost_usd += _try_to_usd(db, cost_try, end_date)

    assignment_stmt = select(PenAssignment).where(
        PenAssignment.assigned_date <= end_date,
        (PenAssignment.removed_date.is_(None)) | (PenAssignment.removed_date >= start_date),
    )
    for assignment in db.scalars(assignment_stmt).all():
        window_start = max(assignment.assigned_date, start_date)
        window_end = min(assignment.removed_date or end_date, end_date)
        if window_start > window_end:
            continue
        weight_stmt = (
            select(WeightRecord)
            .where(
                WeightRecord.animal_id == assignment.animal_id,
                WeightRecord.weigh_date >= window_start,
                WeightRecord.weigh_date <= window_end,
            )
            .order_by(WeightRecord.weigh_date)
        )
        records = list(db.scalars(weight_stmt).all())
        if len(records) < 2:
            continue
        bucket = buckets.get(assignment.pen_id)
        if bucket is None:
            pen = db.get(Pen, assignment.pen_id)
            if pen is None:
                continue
            bucket = _PenEfficiencyBucket(code=pen.code, name=pen.name)
            buckets[assignment.pen_id] = bucket
        bucket.total_weight_gain_kg += records[-1].weight_kg - records[0].weight_kg

    rows: list[PenEfficiencyRead] = []
    for pen_id, bucket in buckets.items():
        gain = float(bucket.total_weight_gain_kg)
        fcr = round(bucket.total_feed_quantity_kg / gain, 2) if gain > 0 else None
        cost_per_kg_try = round(float(bucket.total_feed_cost_try) / gain, 2) if gain > 0 else None
        cost_per_kg_usd = round(float(bucket.total_feed_cost_usd) / gain, 2) if gain > 0 else None
        rows.append(
            PenEfficiencyRead(
                pen_id=pen_id,
                code=bucket.code,
                name=bucket.name,
                total_feed_quantity_kg=round(bucket.total_feed_quantity_kg, 2),
                total_feed_cost_try=_round_money(bucket.total_feed_cost_try),
                total_feed_cost_usd=_round_money(bucket.total_feed_cost_usd),
                total_weight_gain_kg=bucket.total_weight_gain_kg,
                feed_conversion_ratio=fcr,
                cost_per_kg_gain_try=cost_per_kg_try,
                cost_per_kg_gain_usd=cost_per_kg_usd,
            )
        )
    rows.sort(key=lambda r: r.code)
    return rows


def _feed_cost_share_for_animal(
    db: Session, animal_id: uuid.UUID, outcome_date: date, convert_usd: bool = True
) -> tuple[Decimal, Decimal]:
    """Bir hayvanin pen_assignments gecmisindeki (girisinden cikis tarihine
    kadar), o padoga uygulanan rasyon donemleriyle KESISEN gunler icin
    payini hesaplar. Rasyon zaten HAYVAN BASINA tanimli oldugundan (bkz.
    app/modules/feed/models.py RationItem), eski modeldeki gibi o gunku
    padok doluluguna bolme YOKTUR - hayvanin payi direkt olarak
    (rasyon kaleminin hayvan basina gunluk miktari x kesisen gun sayisi)
    x agirlikli ortalama birim maliyettir. Cikistan (satis/olum) sonraki
    hicbir gun bu hesaba dahil edilmez.

    convert_usd=False ise USD kismi hesaplanmaz (0 doner) - cok sayida
    hayvan/kayit uzerinde tek bir istekte calisan raporlarda (surudeki tum
    hayvanlari gezen raporlar) performans/timeout riski olusturur; öyle bir
    ihtiyacta USD, tek bir toplu kurla ayrica hesaplanir (bkz. _asset_book_value)."""
    total_try = Decimal("0")
    total_usd = Decimal("0")
    assignments = list(db.scalars(select(PenAssignment).where(PenAssignment.animal_id == animal_id)).all())
    for assignment in assignments:
        window_end = min(assignment.removed_date or outcome_date, outcome_date)
        if assignment.assigned_date > window_end:
            continue
        rations = db.scalars(
            select(PenRation)
            .options(joinedload(PenRation.items).joinedload(RationItem.unit))
            .where(PenRation.pen_id == assignment.pen_id)
        ).unique().all()
        for ration in rations:
            days = _overlap_days_count(
                assignment.assigned_date, window_end, ration.start_date, ration.end_date or window_end
            )
            if days <= 0:
                continue
            for item in ration.items:
                kg = Decimal(str(_to_kg(item.daily_quantity_per_animal, item.unit.code) * days))
                avg_cost = _feed_avg_cost_per_kg(db, item.feed_item_id, outcome_date)
                if avg_cost is None:
                    continue
                cost_try = kg * avg_cost
                total_try += cost_try
                if convert_usd:
                    total_usd += _try_to_usd(db, cost_try, outcome_date)
    return total_try, total_usd


def _health_cost_try_usd(
    db: Session, animal_id: uuid.UUID, as_of_date: date, convert_usd: bool = True
) -> tuple[Decimal, Decimal]:
    """Bir hayvanin as_of_date'e kadar (o tarih dahil) kayitli tum
    HealthEvent.cost toplami - TL ve USD (her olayin kendi event_date'indeki
    TCMB kuruyla). convert_usd=False ise USD 0 doner (bkz. _feed_cost_share_for_animal)."""
    health_events = list(
        db.scalars(
            select(HealthEvent).where(
                HealthEvent.animal_id == animal_id,
                HealthEvent.cost.isnot(None),
                HealthEvent.event_date <= as_of_date,
            )
        ).all()
    )
    total_try = sum((he.cost for he in health_events), Decimal("0"))
    total_usd = (
        sum((_try_to_usd(db, he.cost, he.event_date) for he in health_events), Decimal("0"))
        if convert_usd
        else Decimal("0")
    )
    return total_try, total_usd


def _accumulated_cost_try_usd(
    db: Session, animal: Animal, as_of_date: date, convert_usd: bool = True
) -> tuple[Decimal, Decimal]:
    """Bir hayvanin girisinden as_of_date'e kadar biriken toplam maliyetini
    (giris degeri + saglik + gun agirlikli yem payi) TL ve USD olarak
    dondurur - "malzeme/stok" durumundaki bir hayvanin defter degeridir
    (bkz. _asset_book_value). Hem Hayvan Karlilik Raporu (_build_profitability_row,
    outcome_date ile) hem _asset_book_value (herhangi bir as_of_date ile)
    bu ortak hesaplamayi kullanir.

    convert_usd=False ise hicbir alt-fact kendi tarihinde TCMB'ye sorulmaz
    (USD 0 doner, sadece TL toplanir) - _asset_book_value gibi SURUDEKI
    TUM hayvanlari tek istekte gezen caller'lar bunu kullanip USD'yi TEK
    bir as_of_date kuruyla toplu hesaplar (performans/timeout riskini
    onlemek icin)."""
    health_cost_try, health_cost_usd = _health_cost_try_usd(db, animal.id, as_of_date, convert_usd)
    feed_cost_try, feed_cost_usd = _feed_cost_share_for_animal(db, animal.id, as_of_date, convert_usd)
    entry_value_try = animal.entry_value or Decimal("0")
    entry_value_usd = (_try_to_usd(db, entry_value_try, animal.entry_date)) if convert_usd else Decimal("0")
    total_try = entry_value_try + health_cost_try + feed_cost_try
    total_usd = entry_value_usd + health_cost_usd + feed_cost_usd
    return total_try, total_usd


def _build_profitability_row(
    db: Session,
    animal: Animal,
    outcome: str,
    outcome_date: date,
    revenue_try: Decimal | None,
) -> AnimalProfitabilityRead:
    health_cost_try, health_cost_usd = _health_cost_try_usd(db, animal.id, outcome_date)
    feed_cost_try, feed_cost_usd = _feed_cost_share_for_animal(db, animal.id, outcome_date)

    entry_value_try = animal.entry_value or Decimal("0")
    entry_value_usd = _try_to_usd(db, entry_value_try, animal.entry_date)

    total_cost_try = entry_value_try + health_cost_try + feed_cost_try
    total_cost_usd = entry_value_usd + health_cost_usd + feed_cost_usd

    revenue_usd = _try_to_usd(db, revenue_try, outcome_date) if revenue_try is not None else None

    profit_try = (revenue_try or Decimal("0")) - total_cost_try
    profit_usd = (revenue_usd or Decimal("0")) - total_cost_usd

    return AnimalProfitabilityRead(
        animal_id=animal.id,
        tag_number=animal.tag_number,
        name=animal.name,
        outcome=outcome,
        outcome_date=outcome_date,
        entry_value_try=animal.entry_value,
        health_cost_try=_round_money(health_cost_try),
        feed_cost_try=_round_money(feed_cost_try),
        total_cost_try=_round_money(total_cost_try),
        total_cost_usd=_round_money(total_cost_usd),
        revenue_try=revenue_try,
        revenue_usd=_round_money(revenue_usd) if revenue_usd is not None else None,
        profit_try=_round_money(profit_try),
        profit_usd=_round_money(profit_usd),
        note=animal.note,
    )


def list_animal_profitability(db: Session, start_date: date, end_date: date) -> list[AnimalProfitabilityRead]:
    """Belirtilen tarih araliginda SATILAN veya OLEN (yani 'kapanmis')
    hayvanlarin YASAM BOYU maliyetini (sadece rapor araligindaki degil,
    girisinden cikisina kadar biriken giris degeri + saglik + yem payi) o
    donemde gerceklesen gelirle (satildiysa) karsilastirir - gelir/maliyet
    eslestirmesi standart muhasebe mantigidir. entry_value, satin alinan
    hayvanlarda odenen tutar, ISLETMEDE DOGANLARDA ise kullanicinin dogum
    aninda bictigi tahmini deger olabilir (biyolojik varlik muhasebesi -
    dogan bir buzagi da bir degerle isletmeye giren bir 'urun'dur; olurse
    bu deger dogrudan zarar yazilir). Aktif hayvanlar bu raporda YOKTUR,
    karliligi henuz gerceklesmedi (Anayasa m.4/m.5)."""
    rows: list[AnimalProfitabilityRead] = []

    sale_stmt = select(Sale).options(joinedload(Sale.animal)).where(
        Sale.sale_date >= start_date, Sale.sale_date <= end_date
    )
    for sale in db.scalars(sale_stmt).all():
        rows.append(_build_profitability_row(db, sale.animal, "Satıldı", sale.sale_date, sale.total_amount))

    death_stmt = select(Death).options(joinedload(Death.animal)).where(
        Death.death_date >= start_date, Death.death_date <= end_date
    )
    for death in db.scalars(death_stmt).all():
        rows.append(_build_profitability_row(db, death.animal, "Öldü", death.death_date, None))

    rows.sort(key=lambda r: r.profit_try)
    return rows


def list_herd_cost_summary(db: Session, start_date: date, end_date: date) -> list[HerdCostSummaryRead]:
    """Belirtilen tarih araliginda GERCEKLESEN (dagitilan/kaydedilen/satilan)
    tum maliyet ve gelir kalemlerini TL ve USD olarak ozetler - donemsel
    genel bakis/planlama icindir (Hayvan Kârlılık Raporu'ndaki 'yasam boyu'
    eslestirmesinden farkli olarak, burada sadece SECILEN DONEMDE olusan
    tutarlar toplanir)."""
    feed_try = feed_usd = Decimal("0")
    rations = _rations_overlapping(db, start_date, end_date)
    assignments_by_pen_for_cost: dict[int, list[PenAssignment]] = {}
    for pen_id in {r.pen_id for r in rations}:
        assignments_by_pen_for_cost[pen_id] = list(
            db.scalars(select(PenAssignment).where(PenAssignment.pen_id == pen_id)).all()
        )
    for ration in rations:
        overlap_start = max(ration.start_date, start_date)
        overlap_end = min(ration.end_date or end_date, end_date)
        if overlap_start > overlap_end:
            continue
        headcounts = _daily_headcounts(assignments_by_pen_for_cost[ration.pen_id], overlap_start, overlap_end)
        for item in ration.items:
            per_animal_kg = _to_kg(item.daily_quantity_per_animal, item.unit.code)
            total_kg = sum(per_animal_kg * count for count in headcounts.values())
            avg_cost = _feed_avg_cost_per_kg(db, item.feed_item_id, end_date)
            if avg_cost is None:
                continue
            cost_try = Decimal(str(total_kg)) * avg_cost
            feed_try += cost_try
            feed_usd += _try_to_usd(db, cost_try, end_date)

    health_try = health_usd = Decimal("0")
    health_stmt = select(HealthEvent).where(
        HealthEvent.event_date >= start_date, HealthEvent.event_date <= end_date, HealthEvent.cost.isnot(None)
    )
    for he in db.scalars(health_stmt).all():
        health_try += he.cost
        health_usd += _try_to_usd(db, he.cost, he.event_date)

    entry_value_try = entry_value_usd = Decimal("0")
    entry_value_stmt = select(Animal).where(
        Animal.entry_date >= start_date, Animal.entry_date <= end_date, Animal.entry_value.isnot(None)
    )
    for animal in db.scalars(entry_value_stmt).all():
        entry_value_try += animal.entry_value
        entry_value_usd += _try_to_usd(db, animal.entry_value, animal.entry_date)

    revenue_try = revenue_usd = Decimal("0")
    sale_stmt = select(Sale).where(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
    for sale in db.scalars(sale_stmt).all():
        revenue_try += sale.total_amount
        revenue_usd += _try_to_usd(db, sale.total_amount, sale.sale_date)

    total_cost_try = feed_try + health_try + entry_value_try
    total_cost_usd = feed_usd + health_usd + entry_value_usd

    def row(category: str, category_code: str, try_amount: Decimal, usd_amount: Decimal) -> HerdCostSummaryRead:
        return HerdCostSummaryRead(
            category=category,
            category_code=category_code,
            amount_try=_round_money(try_amount),
            amount_usd=_round_money(usd_amount),
        )

    return [
        row("Yem Maliyeti", "FEED", feed_try, feed_usd),
        row("Sağlık/Tedavi Maliyeti", "HEALTH", health_try, health_usd),
        row("Giriş Değeri (Alım/Doğum)", "ENTRY_VALUE", entry_value_try, entry_value_usd),
        row("Toplam Maliyet", "TOTAL_COST", total_cost_try, total_cost_usd),
        row("Satış Geliri", "REVENUE", revenue_try, revenue_usd),
        row("Net (Gelir - Maliyet)", "NET", revenue_try - total_cost_try, revenue_usd - total_cost_usd),
    ]


# --- Demirbaş (amortisman) / Malzeme sınıflandırması ---
#
# Biyolojik varlık muhasebesi (IAS 41 pratiği): inek/damızlık boğa bir
# DURAN VARLIK (demirbaş) gibi amortismana tabidir; büyümekte olan bir
# buzağı ise bir STOK/MALZEME gibi sadece maliyet biriktirir (bkz.
# _accumulated_cost_try_usd). Sınıflandırma hiçbir yerde SAKLANMAZ -
# PregnancyCheck/BreedingEvent gecmisinden her istek aninda turetilir
# (Anayasa m.4/m.5).


def _first_confirmed_pregnancy_date(db: Session, animal_id: uuid.UUID) -> date | None:
    """Bir disi hayvana (dam) ait TUM PregnancyCheck kayitlari arasinda
    sonucu 'GEBE' olan EN ERKEN check_date - bu, hayvanin 'malzeme'den
    'demirbasa' gectigi andir. _classify_female'in aksine yalnizca AKTIF
    tohumlama dongusune degil hayvanin TUM gecmisine bakar: bir kez gebe
    kaldiysa (o dongu daha sonra bos/kaybedilmis olsa bile) bir daha
    malzemeye donmez."""
    stmt = (
        select(func.min(PregnancyCheck.check_date))
        .select_from(PregnancyCheck)
        .join(BreedingEvent, PregnancyCheck.breeding_event_id == BreedingEvent.id)
        .join(PregnancyResult, PregnancyCheck.result_id == PregnancyResult.id)
        .where(BreedingEvent.dam_id == animal_id, PregnancyResult.code == CONFIRMED_PREGNANCY_RESULT_CODE)
    )
    return db.scalar(stmt)


def _bull_transition_date(db: Session, animal: Animal) -> date | None:
    """Bir erkek hayvanin 'malzeme'den 'demirbasa' (damizlik boga) gectigi
    an: satin alindiysa giristen itibaren (Satin Alma = zaten boga olarak
    alindigi varsayilir); suruden dogduysa, ilk kez bir Tohumlama kaydinda
    dogal asim bogasi (sire_animal_id) olarak kullanildigi tarih."""
    if animal.entry_source.code == PURCHASE_ENTRY_SOURCE_CODE:
        return animal.entry_date
    return db.scalar(
        select(func.min(BreedingEvent.service_date)).where(BreedingEvent.sire_animal_id == animal.id)
    )


def _asset_transition_date(db: Session, animal: Animal) -> date | None:
    if animal.gender.code == FEMALE_GENDER_CODE:
        return _first_confirmed_pregnancy_date(db, animal.id)
    if animal.gender.code == MALE_GENDER_CODE:
        return _bull_transition_date(db, animal)
    return None


def _asset_book_value(
    db: Session, animal: Animal, as_of_date: date, as_of_rate: Decimal | None = None
) -> tuple[Decimal, Decimal, str]:
    """Bir hayvanin as_of_date'teki defter degerini (TL, USD) ve durumunu
    ("Demirbaş" | "Malzeme") dondurur.

    Malzeme: _accumulated_cost_try_usd (giris degeri + saglik + yem payi),
    TEK bir as_of_date kuruyla USD'ye cevrilir.

    Demirbaş: transition anindaki malzeme maliyeti (USD'ye o gunun TCMB
    kuruyla cevrilir) acilis degeri olur; %50 hurda deger, 10 yil faydali
    omur ile duz-hat (straight-line) amortisman USD uzerinden islenir;
    TL karsiligi as_of_date'teki (aciliftaki degil) GUNCEL kurla verilir -
    "bu hayvan bugun TL olarak ne degerde" sorusuna cevap versin diye.

    PERFORMANS: Hayvan Kârlılık Raporu'nun aksine (orada her fact kendi
    tarihindeki kurla cevrilir - bkz. _accumulated_cost_try_usd docstring),
    bu fonksiyon SURUDEKI TUM hayvanlar icin tek istekte cagrildigindan
    (bkz. list_herd_animal_market_values) alt-fact'lerin USD donusumu
    KAPATILIR (convert_usd=False) ve yerine
    TEK bir as_of_date kuru kullanilir -
    aksi halde her hayvanin her giris/saglik/yem tarihi icin ayri bir TCMB
    sorgusu tetiklenip rapor onlarca-yuzlerce ag cagrisiyla zaman asimina
    ugrar (gercek bir prodüksiyon hatasi olarak gözlemlendi). as_of_rate
    caller tarafindan onceden cekilip tum hayvanlar icin yeniden kullanilir
    (verilmezse burada tek seferlik cekilir)."""
    if as_of_rate is None:
        as_of_rate = fx_service.get_usd_try_rate(db, as_of_date)

    transition_date = _asset_transition_date(db, animal)
    if transition_date is None or as_of_date < transition_date:
        total_try, _ = _accumulated_cost_try_usd(db, animal, as_of_date, convert_usd=False)
        total_usd = total_try / as_of_rate if as_of_rate else Decimal("0")
        return _round_money(total_try), _round_money(total_usd), "Malzeme"

    acquisition_try, _ = _accumulated_cost_try_usd(db, animal, transition_date, convert_usd=False)
    transition_rate = fx_service.get_usd_try_rate(db, transition_date)
    acquisition_usd = acquisition_try / transition_rate if transition_rate else Decimal("0")

    residual_usd = acquisition_usd * DEPRECIATION_RESIDUAL_RATIO
    depreciable_usd = acquisition_usd - residual_usd
    years_elapsed = Decimal((as_of_date - transition_date).days) / Decimal("365")
    accumulated_depreciation_usd = min(
        depreciable_usd * years_elapsed / DEPRECIATION_USEFUL_LIFE_YEARS, depreciable_usd
    )
    book_value_usd = acquisition_usd - accumulated_depreciation_usd
    book_value_try = book_value_usd * as_of_rate if as_of_rate else Decimal("0")

    return _round_money(book_value_try), _round_money(book_value_usd), "Demirbaş"


def _animals_alive_at(db: Session, as_of_date: date) -> list[Animal]:
    """as_of_date'te (o tarihte) yasayan hayvanlar. Animal.status_id sadece
    GUNCEL durumu tutar (Anayasa m.8 - anlik yansima), gecmis bir tarihteki
    durumu degil - bu yuzden dogrudan Sale/Death tablolarinin tarihlerine
    bakilir: entry_date <= as_of_date VE o tarihe kadar satilmamis/olmemis."""
    sold_ids = set(
        db.scalars(select(Sale.animal_id).where(Sale.sale_date <= as_of_date)).all()
    )
    dead_ids = set(
        db.scalars(select(Death.animal_id).where(Death.death_date <= as_of_date)).all()
    )
    closed_ids = sold_ids | dead_ids
    stmt = select(Animal).options(joinedload(Animal.gender), joinedload(Animal.entry_source)).where(
        Animal.entry_date <= as_of_date
    )
    return [a for a in db.scalars(stmt).all() if a.id not in closed_ids]


# --- Tahmini Piyasa Değeri (büyüme çıpaları) ---
#
# _asset_book_value (yukarida) SAF MALIYET muhasebesidir. Burasi ona
# PARALEL, ayri bir gosterge:
#   - Malzeme durumundaki (henuz Demirbasa gecmemis) genc hayvanlar icin,
#     kullanicinin GrowthValuationCheckpoint olarak TL cinsinden girdigi
#     yas-bazli piyasa fiyatlari (AGE_3/6/9/12) arasinda lineer
#     interpolasyon yapilir.
#   - Demirbasa gecmis (olgun) bir DISI icin, GUNCEL ureme durumuna
#     (Gebe/Bos) gore GEBE/BOS cipasi kullanilir.
# Ikisinde de sistem bir oran/egri TAHMIN ETMEZ (Anayasa m.4) - sadece
# kullanicinin girdigi TL degerleri arasinda toplar/aralar; USD karsiligi
# rapor uretilirken as_of_date'teki TCMB kuruyla turetilir (Anayasa m.5 -
# tipki entry_value/saglik/yem maliyetleri gibi). Cipa girilmemisse
# (veya erkek icin Demirbas donemindeyse - erkek/boga icin olgun-donem
# piyasa cipasi yoktur), mevcut maliyet-bazli _asset_book_value'ya geri
# duser (kaynagi source_code alaninda acikca belirtilir).

_AGE_CATEGORY_TO_MONTHS = {"AGE_3": 3, "AGE_6": 6, "AGE_9": 9, "AGE_12": 12}
_MATURE_FEMALE_STATUS_CODES = ("GEBE", "BOS")


def _checkpoint_maps(db: Session) -> tuple[dict[str, dict[int, Decimal]], dict[str, dict[str, Decimal]]]:
    """(buyume_cipalari, olgun_disi_cipalari) dondurur - ikisi de
    gender_code anahtarlidir. buyume_cipalari: {age_months: value_try};
    olgun_disi_cipalari: {"GEBE"|"BOS": value_try} (bkz. modul docstring'i)."""
    stmt = select(GrowthValuationCheckpoint).options(joinedload(GrowthValuationCheckpoint.gender))
    growth: dict[str, dict[int, Decimal]] = {}
    mature: dict[str, dict[str, Decimal]] = {}
    for checkpoint in db.scalars(stmt).all():
        gender_code = checkpoint.gender.code
        if checkpoint.category_code in _AGE_CATEGORY_TO_MONTHS:
            growth.setdefault(gender_code, {})[_AGE_CATEGORY_TO_MONTHS[checkpoint.category_code]] = checkpoint.value_try
        elif checkpoint.category_code in _MATURE_FEMALE_STATUS_CODES:
            mature.setdefault(gender_code, {})[checkpoint.category_code] = checkpoint.value_try
    return growth, mature


def _interpolate_market_value_try(entry_value_try: Decimal, checkpoints: dict[int, Decimal], age_days: int) -> Decimal:
    """(0 gun, entry_value_try) noktasini ve doldurulmus yas cipalarini
    (kucukten buyuge) gezip age_days'e karsilik gelen TL degerini lineer
    interpolasyonla dondurur. Son doldurulan cipadan sonra deger sabit
    tutulur - ileriye tahmin yapilmaz (bkz. modul docstring'i)."""
    points = sorted((age_months * GROWTH_CHECKPOINT_DAYS_PER_MONTH, value) for age_months, value in checkpoints.items())
    prev_days, prev_value = 0, entry_value_try
    for days, value in points:
        if age_days <= days:
            if days == prev_days:
                return value
            ratio = Decimal(age_days - prev_days) / Decimal(days - prev_days)
            return prev_value + (value - prev_value) * ratio
        prev_days, prev_value = days, value
    return prev_value


def _is_currently_pregnant(db: Session, animal_id: uuid.UUID) -> bool:
    """Hayvanin en son tohumlama dongusunde onaylanmis (GEBE) bir gebelik
    kontrolu var mi - bkz. _classify_female'deki ayni kontrolun sadelestirilmis
    hali. NOT: zaman serisi raporlarinda GECMIS tarihler icin de bu GUNCEL
    durum kullanilir (kasitli basitlestirme) - o tarihte gercekten gebe/acik
    olup olmadigini yeniden insa etmek ayri bir tarihsel siniflandirma
    gerektirir; bkz. _market_value_estimate_try caller'i."""
    latest_event = db.scalar(
        select(BreedingEvent).where(BreedingEvent.dam_id == animal_id).order_by(BreedingEvent.service_date.desc()).limit(1)
    )
    if latest_event is None:
        return False
    latest_check = db.scalar(
        select(PregnancyCheck)
        .options(joinedload(PregnancyCheck.result))
        .where(PregnancyCheck.breeding_event_id == latest_event.id)
        .order_by(PregnancyCheck.check_date.desc())
        .limit(1)
    )
    return latest_check is not None and latest_check.result.code == CONFIRMED_PREGNANCY_RESULT_CODE


def _market_value_estimate_try(
    db: Session,
    animal: Animal,
    as_of_date: date,
    growth_checkpoints_by_gender: dict[str, dict[int, Decimal]],
    mature_checkpoints_by_gender: dict[str, dict[str, Decimal]],
) -> Decimal | None:
    """Bir hayvanin buyume cipalarina (veya olgun disi icin Gebe/Bos
    cipasina) gore tahmini piyasa degeri (TL); cipa girilmemisse VEYA
    (erkek + Demirbas donemi gibi) uygulanamaz bir durumsa None doner
    (caller maliyet-bazli degere geri duser)."""
    transition_date = _asset_transition_date(db, animal)
    if transition_date is not None and as_of_date >= transition_date:
        if animal.gender.code != FEMALE_GENDER_CODE:
            return None
        mature_checkpoints = mature_checkpoints_by_gender.get(FEMALE_GENDER_CODE)
        if not mature_checkpoints:
            return None
        status_code = "GEBE" if _is_currently_pregnant(db, animal.id) else "BOS"
        return mature_checkpoints.get(status_code)

    checkpoints = growth_checkpoints_by_gender.get(animal.gender.code)
    if not checkpoints:
        return None
    age_days = (as_of_date - animal.entry_date).days
    if age_days < 0:
        return None
    entry_value_try = animal.entry_value or Decimal("0")
    return _interpolate_market_value_try(entry_value_try, checkpoints, age_days)


def _estimated_market_value_usd_try(
    db: Session,
    animal: Animal,
    as_of_date: date,
    growth_checkpoints_by_gender: dict[str, dict[int, Decimal]],
    mature_checkpoints_by_gender: dict[str, dict[str, Decimal]],
    as_of_rate: Decimal | None,
) -> tuple[Decimal, Decimal, str]:
    """'Tahmini Piyasa Değeri' göstergesi (TL, USD, kaynak). Çıpa
    üzerinden hesaplanabiliyorsa onu (TL, kullanıcının girdiği gibi - USD
    karşılığı as_of_date'teki TCMB kuruyla TEK seferde türetilir), aksi
    halde mevcut maliyet-bazlı _asset_book_value'yu kullanır - source_code
    hangisinin kullanıldığını açıkça belirtir."""
    if as_of_rate is None:
        as_of_rate = fx_service.get_usd_try_rate(db, as_of_date)

    market_try = _market_value_estimate_try(db, animal, as_of_date, growth_checkpoints_by_gender, mature_checkpoints_by_gender)
    if market_try is not None:
        market_usd = market_try / as_of_rate if as_of_rate else Decimal("0")
        return _round_money(market_try), _round_money(market_usd), "market_estimate"

    book_try, book_usd, _ = _asset_book_value(db, animal, as_of_date, as_of_rate)
    return book_try, book_usd, "cost_basis"


def list_herd_animal_market_values(db: Session, as_of_date: date) -> list[AnimalMarketValueRead]:
    """as_of_date itibariyla YAŞAYAN tüm hayvanların 'Tahmini Piyasa
    Değeri'ni TEK TEK listeler (bkz. _estimated_market_value_usd_try) -
    hayvan hayvan bir döküm verir. Alım/satım öncesi birden fazla hayvanı bir
    arada değerlendirmek için (kullanıcı arayüzünde istediği satırları
    seçip toplamını görebilir - bu seçim/toplam client-side yapılır,
    burada sadece tam liste döner)."""
    growth_checkpoints_by_gender, mature_checkpoints_by_gender = _checkpoint_maps(db)
    rate = fx_service.get_usd_try_rate(db, as_of_date)
    rows: list[AnimalMarketValueRead] = []
    for animal in _animals_alive_at(db, as_of_date):
        amount_try, amount_usd, source_code = _estimated_market_value_usd_try(
            db, animal, as_of_date, growth_checkpoints_by_gender, mature_checkpoints_by_gender, rate
        )
        age_months = full_months_between(animal.birth_date, as_of_date) if animal.birth_date else None
        rows.append(
            AnimalMarketValueRead(
                animal_id=animal.id,
                tag_number=animal.tag_number,
                name=animal.name,
                gender_name=animal.gender.name,
                age_months=age_months,
                amount_try=amount_try,
                amount_usd=amount_usd,
                source_code=source_code,
            )
        )
    rows.sort(key=lambda r: (r.age_months is None, -(r.age_months or 0)))
    return rows
