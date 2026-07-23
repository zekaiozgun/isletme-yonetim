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
from sqlalchemy.orm import Session, joinedload

from app.core.date_utils import full_months_between
from app.core.lookup_helpers import get_lookup_by_code
from app.modules.animal.lookups import AnimalStatus, EntrySource, Gender
from app.modules.animal.models import Animal
from app.modules.breeding.models import BreedingEvent, PregnancyCheck
from app.modules.genetic_resource.models import SemenBatch
from app.modules.death.models import Death
from app.modules.feed.models import FeedDistribution, FeedItem
from app.modules.health.models import HealthEvent
from app.modules.sale.models import Sale
from app.modules.weight.models import WeightRecord
from app.modules.pen.models import Pen, PenAssignment
from app.modules.reports.schemas import (
    BredAnimalRead,
    BreedingCandidateRead,
    BreedingPerformanceRead,
    CalvingIntervalRead,
    CalvingRead,
    DashboardSummaryRead,
    DeathLossReportRead,
    FeedConsumptionRead,
    HealthEventReportRead,
    HerdFlowReportRead,
    HerdInventoryRead,
    PenOccupancyRead,
    PregnancyCheckResultRead,
    PregnantAnimalRead,
    RepeatBreederRead,
    SalesReportRead,
    WeightGainRead,
    YoungAnimalRead,
)

FEMALE_GENDER_CODE = "DISI"
MALE_GENDER_CODE = "ERKEK"
ACTIVE_STATUS_CODE = "AKTIF"
DIFFICULT_BIRTH_TYPE_CODE = "GUC"
ILLNESS_EVENT_TYPE_CODE = "HASTALIK_BILDIRIMI"
FEED_TON_UNIT_CODE = "TON"

BREEDING_AGE_MONTHS = 12
POSTPARTUM_WAIT_DAYS = 45
PREGNANCY_CHECK_DUE_DAYS = 45
CALF_MAX_MONTHS = 7
GESTATION_DAYS = 283


def _latest_breeding_by_dam(db: Session) -> dict[uuid.UUID, BreedingEvent]:
    stmt = select(BreedingEvent).options(joinedload(BreedingEvent.service_method)).order_by(BreedingEvent.service_date)
    latest: dict[uuid.UUID, BreedingEvent] = {}
    for event in db.scalars(stmt).all():
        latest[event.dam_id] = event  # siralamadan dolayi son atama en yeni olur
    return latest


def _latest_calving_by_dam(db: Session) -> dict[uuid.UUID, date]:
    stmt = (
        select(Animal.mother_id, func.max(Animal.birth_date))
        .where(Animal.mother_id.isnot(None), Animal.birth_date.isnot(None))
        .group_by(Animal.mother_id)
    )
    return {mother_id: birth_date for mother_id, birth_date in db.execute(stmt).all()}


def _latest_check_by_event(db: Session) -> dict[int, PregnancyCheck]:
    stmt = select(PregnancyCheck).options(joinedload(PregnancyCheck.result)).order_by(PregnancyCheck.check_date)
    latest: dict[int, PregnancyCheck] = {}
    for check in db.scalars(stmt).all():
        latest[check.breeding_event_id] = check
    return latest


@dataclass
class _Classification:
    kind: str  # "candidate_new" | "candidate_postpartum" | "pending" | "suspicious" | "pregnant" | "open" | "none"
    breeding_event: BreedingEvent | None = None
    last_calving_date: date | None = None


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
        return _Classification(kind="none")

    if last_calving is not None and last_calving > last_breed.service_date:
        days_since_calving = (today - last_calving).days
        if days_since_calving >= POSTPARTUM_WAIT_DAYS:
            return _Classification(kind="candidate_postpartum", last_calving_date=last_calving)
        return _Classification(kind="none")

    check = latest_check_by_event.get(last_breed.id)
    if check is None:
        return _Classification(kind="pending", breeding_event=last_breed)
    result_code = check.result.code
    if result_code == "GEBE":
        return _Classification(kind="pregnant", breeding_event=last_breed)
    if result_code == "BOS":
        return _Classification(kind="open", breeding_event=last_breed)
    return _Classification(kind="suspicious", breeding_event=last_breed)


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
    "candidate_postpartum": "Doğum Sonrası",
    "open": "Tekrar Kızgınlık / Boş",
}
_BREEDING_CANDIDATE_REASON_ORDER = {"candidate_new": 0, "candidate_postpartum": 1, "open": 2}


def list_breeding_candidates(db: Session, today: date | None = None) -> list[BreedingCandidateRead]:
    today = today or date.today()
    entries: list[tuple[int, BreedingCandidateRead]] = []
    for animal, classification in _classify_all_active_females(db, today):
        if classification.kind not in _BREEDING_CANDIDATE_REASONS:
            continue
        last_service_date = None
        if classification.kind == "open":
            assert classification.breeding_event is not None
            last_service_date = classification.breeding_event.service_date
        row = BreedingCandidateRead(
            animal_id=animal.id,
            tag_number=animal.tag_number,
            name=animal.name,
            birth_date=animal.birth_date,
            age_months=full_months_between(animal.birth_date, today) if animal.birth_date else None,
            reason=_BREEDING_CANDIDATE_REASONS[classification.kind],
            last_calving_date=classification.last_calving_date,
            last_service_date=last_service_date,
        )
        entries.append((_BREEDING_CANDIDATE_REASON_ORDER[classification.kind], row))
    entries.sort(key=lambda e: (e[0], e[1].tag_number))
    return [row for _, row in entries]


def list_bred_animals(db: Session, today: date | None = None) -> list[BredAnimalRead]:
    today = today or date.today()
    rows: list[BredAnimalRead] = []
    for animal, classification in _classify_all_active_females(db, today):
        if classification.kind not in ("pending", "suspicious", "pregnant"):
            continue
        event = classification.breeding_event
        assert event is not None
        days_since_service = (today - event.service_date).days
        if classification.kind == "pending":
            check_status = "Kontrol Bekliyor"
            check_due = days_since_service >= PREGNANCY_CHECK_DUE_DAYS
            expected_calving = None
        elif classification.kind == "suspicious":
            check_status = "Şüpheli (Tekrar Kontrol Gerekli)"
            check_due = True
            expected_calving = None
        else:
            check_status = "Gebe"
            check_due = False
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
            )
        )

    def sort_key(row: BredAnimalRead) -> tuple[int, object]:
        if row.pregnancy_check_due and row.check_status != "Gebe":
            return (0, -row.days_since_service)
        if row.check_status == "Kontrol Bekliyor":
            return (1, row.service_date)
        if row.check_status == "Gebe":
            return (2, row.service_date)
        return (3, row.service_date)

    rows.sort(key=sort_key)
    return rows


def list_repeat_breeders(db: Session, today: date | None = None) -> list[RepeatBreederRead]:
    today = today or date.today()
    rows: list[RepeatBreederRead] = []
    for animal, classification in _classify_all_active_females(db, today):
        if classification.kind != "open":
            continue
        event = classification.breeding_event
        assert event is not None
        rows.append(
            RepeatBreederRead(
                animal_id=animal.id,
                tag_number=animal.tag_number,
                name=animal.name,
                last_service_date=event.service_date,
                days_open=(today - event.service_date).days,
                service_method_name=event.service_method.name,
            )
        )
    rows.sort(key=lambda r: -r.days_open)
    return rows


def list_pregnant_animals(db: Session, today: date | None = None) -> list[PregnantAnimalRead]:
    today = today or date.today()
    rows: list[PregnantAnimalRead] = []
    for animal, classification in _classify_all_active_females(db, today):
        if classification.kind != "pregnant":
            continue
        event = classification.breeding_event
        assert event is not None
        expected_calving = event.service_date + timedelta(days=GESTATION_DAYS)
        rows.append(
            PregnantAnimalRead(
                animal_id=animal.id,
                tag_number=animal.tag_number,
                name=animal.name,
                service_date=event.service_date,
                expected_calving_date=expected_calving,
                days_until_calving=(expected_calving - today).days,
            )
        )
    rows.sort(key=lambda r: r.expected_calving_date)
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
            )
        )
    return rows


def list_calving_intervals(db: Session) -> list[CalvingIntervalRead]:
    """Her inek icin gecmisteki TUM dogumlarini (Animal.mother_id + birth_date)
    tarihe gore siralayip son iki dogum arasindaki gun farkini (yavrulama
    araligi) hesaplar. Tarih araligi gerektirmez - sureklilik gosteren, yavas
    degisen bir verimlilik gostergesidir (Anayasa m.4/m.5: hicbir yerde
    saklanmaz, her istek Animal.birth_date/mother_id'den turetilir)."""
    stmt = (
        select(Animal.mother_id, Animal.birth_date)
        .where(Animal.mother_id.isnot(None), Animal.birth_date.isnot(None))
        .order_by(Animal.mother_id, Animal.birth_date)
    )
    calving_dates_by_dam: dict[uuid.UUID, list[date]] = {}
    for mother_id, birth_date in db.execute(stmt).all():
        calving_dates_by_dam.setdefault(mother_id, []).append(birth_date)

    dam_ids = list(calving_dates_by_dam.keys())
    dams = {a.id: a for a in db.scalars(select(Animal).where(Animal.id.in_(dam_ids))).all()} if dam_ids else {}

    dam_rows: list[CalvingIntervalRead] = []
    for dam_id, dates in calving_dates_by_dam.items():
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
    distribution_count: int = 0


def list_feed_consumption(db: Session, start_date: date, end_date: date) -> list[FeedConsumptionRead]:
    """Belirtilen tarih araliginda (distribution_date) padok + yem urunu bazinda
    dagitilan toplam yem miktari (kg'a normalize edilerek, ton kayitlari x1000)."""
    stmt = (
        select(FeedDistribution)
        .options(
            joinedload(FeedDistribution.pen),
            joinedload(FeedDistribution.feed_item).joinedload(FeedItem.feed_type),
            joinedload(FeedDistribution.unit),
        )
        .where(FeedDistribution.distribution_date >= start_date, FeedDistribution.distribution_date <= end_date)
    )
    buckets: dict[tuple[int, int], _FeedBucket] = {}
    for dist in db.scalars(stmt).all():
        key = (dist.pen_id, dist.feed_item_id)
        bucket = buckets.get(key)
        if bucket is None:
            bucket = _FeedBucket(
                pen_code=dist.pen.code,
                pen_name=dist.pen.name,
                feed_item_name=dist.feed_item.name,
                feed_type_name=dist.feed_item.feed_type.name,
            )
            buckets[key] = bucket
        quantity_kg = float(dist.quantity) * (1000 if dist.unit.code == FEED_TON_UNIT_CODE else 1)
        bucket.total_quantity_kg += quantity_kg
        bucket.distribution_count += 1

    rows = [
        FeedConsumptionRead(
            pen_code=b.pen_code,
            pen_name=b.pen_name,
            feed_item_name=b.feed_item_name,
            feed_type_name=b.feed_type_name,
            total_quantity_kg=round(b.total_quantity_kg, 2),
            distribution_count=b.distribution_count,
        )
        for b in buckets.values()
    ]
    rows.sort(key=lambda r: -r.total_quantity_kg)
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
        rows.append(HerdFlowReportRead(category=f"Giriş - {name}", direction="Giriş", count=count))
        total_in += count

    rows.append(HerdFlowReportRead(category="Çıkış - Satış", direction="Çıkış", count=sale_count))
    rows.append(HerdFlowReportRead(category="Çıkış - Ölüm", direction="Çıkış", count=death_count))
    total_out = sale_count + death_count

    rows.append(HerdFlowReportRead(category="Net Değişim", direction="Net", count=total_in - total_out))
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
    return rows


def _active_animals_with_age(db: Session, today: date) -> list[tuple[Animal, int]]:
    active_id = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE).id
    stmt = (
        select(Animal)
        .options(joinedload(Animal.gender), joinedload(Animal.mother))
        .where(Animal.status_id == active_id, Animal.birth_date.isnot(None))
        .order_by(Animal.birth_date)
    )
    return [(a, full_months_between(a.birth_date, today)) for a in db.scalars(stmt).all()]


def list_active_animals(db: Session, today: date | None = None) -> list[YoungAnimalRead]:
    """Tum aktif hayvanlar (dogum tarihi bilinmeyenler dahil) - calves/
    heifers-steers'in aksine yas araligina gore filtrelemez."""
    today = today or date.today()
    active_id = get_lookup_by_code(db, AnimalStatus, ACTIVE_STATUS_CODE).id
    stmt = (
        select(Animal)
        .options(joinedload(Animal.gender), joinedload(Animal.mother))
        .where(Animal.status_id == active_id)
        .order_by(Animal.tag_number)
    )
    rows: list[YoungAnimalRead] = []
    for animal in db.scalars(stmt).all():
        age_months = full_months_between(animal.birth_date, today) if animal.birth_date else None
        rows.append(
            YoungAnimalRead(
                animal_id=animal.id,
                tag_number=animal.tag_number,
                name=animal.name,
                gender_name=animal.gender.name,
                birth_date=animal.birth_date,
                age_months=age_months,
                age_days=(today - animal.birth_date).days if animal.birth_date else None,
                mother_tag_number=animal.mother.tag_number if animal.mother else None,
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
        birth_date=animal.birth_date,
        age_months=age_months,
        age_days=(today - animal.birth_date).days if animal.birth_date else None,
        mother_tag_number=animal.mother.tag_number if animal.mother else None,
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

    yearly_losses = list_death_losses(db, today - timedelta(days=365), today, today)
    total_deaths = sum(r.death_count for r in yearly_losses)
    total_active_for_loss = sum(r.current_active_count for r in yearly_losses)
    annual_loss_rate = (
        round(total_deaths / (total_deaths + total_active_for_loss) * 100, 1)
        if (total_deaths + total_active_for_loss) > 0
        else None
    )

    return DashboardSummaryRead(
        active_animal_count=inventory.total_active,
        breeding_candidate_count=len(list_breeding_candidates(db, today)),
        pregnancy_check_due_count=sum(1 for b in bred_animals if b.pregnancy_check_due),
        pregnant_count=sum(1 for b in bred_animals if b.check_status == "Gebe"),
        repeat_breeder_count=len(list_repeat_breeders(db, today)),
        calves_count=inventory.calves_count,
        heifers_steers_count=inventory.heifers_steers_count,
        pen_occupancy_rate=pen_occupancy_rate,
        average_calving_interval_days=average_calving_interval,
        annual_loss_rate=annual_loss_rate,
    )
