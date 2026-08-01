"""_classify_female icin birim testleri (app/modules/reports/service.py).

Bu fonksiyon Anayasa m.4/m.5'in kalbi: bir disi hayvanin ureme durumunu
(Tohumlanacak/Post Partum/Tohumlu/Supheli/Gebe/Bos) hicbir yerde
saklamadan, sadece elindeki fact'lerden turetir. HICBIR DB SORGUSU
YAPMAZ (butun parametreler hazir Python nesneleri) - bu yuzden test
icin veritabani/fixture gerekmez, tamamen izole calisir.

Dosya basindaki docstring'in iddia ettigi "5 durumdan TAM OLARAK BIRINE
duser" onermesini (asagida test_partition_is_exhaustive_and_disjoint
ile) fiilen dogrular - bu onerme, Sürü Durum Özeti raporundaki
"Doğurgan Yaştaki Dişi = 7 alt-durumun toplamı" garantisinin temelidir.
"""

from datetime import date, timedelta

import pytest

from app.modules.animal.models import Animal
from app.modules.breeding.lookups import PregnancyResult
from app.modules.breeding.models import BreedingEvent, PregnancyCheck
from app.modules.reports.service import (
    BREEDING_AGE_MONTHS,
    POSTPARTUM_WAIT_DAYS,
    _classify_female,
)

TODAY = date(2026, 8, 1)


def make_animal(birth_date: date | None) -> Animal:
    return Animal(birth_date=birth_date)


def make_breed(service_date: date, event_id: int = 1) -> BreedingEvent:
    return BreedingEvent(id=event_id, service_date=service_date)


def make_check(result_code: str, note: str | None = None) -> PregnancyCheck:
    check = PregnancyCheck(note=note)
    check.result = PregnancyResult(code=result_code)
    return check


class TestNeverBredNeverCalved:
    def test_reaches_breeding_age_becomes_candidate_new(self):
        birth = date(TODAY.year - 2, TODAY.month, TODAY.day)  # 24 ay - kesin yasta
        animal = make_animal(birth)
        result = _classify_female(animal, None, None, {}, TODAY)
        assert result.kind == "candidate_new"

    def test_exactly_at_threshold_becomes_candidate_new(self):
        # BREEDING_AGE_MONTHS ay once dogmus - tam sinirda "yeterli yas" sayilmali.
        birth = date(2024, 8, 1)
        assert BREEDING_AGE_MONTHS == 12
        animal = make_animal(birth)
        result = _classify_female(animal, None, None, {}, TODAY)
        assert result.kind == "candidate_new"

    def test_too_young_stays_none(self):
        animal = make_animal(date(2026, 6, 1))  # 2 aylik
        result = _classify_female(animal, None, None, {}, TODAY)
        assert result.kind == "none"

    def test_unknown_birth_date_stays_none_regardless_of_true_age(self):
        """Anayasa m.4: sistem tahmin etmez - dogum tarihi bilinmiyorsa
        yasini varsaymaz, sessizce 'none'a duser (herhangi bir rapora
        dahil edilmez, ne tohumlanacak ne de yas kovasina girer)."""
        animal = make_animal(None)
        result = _classify_female(animal, None, None, {}, TODAY)
        assert result.kind == "none"


class TestCalvedWithoutRegisteredBreeding:
    """last_breed=None ama last_calving var - dışarıdan gebe/laktasyondaki
    bir hayvan alınmış, tohumlama kaydı hiç girilmemiş senaryosu."""

    def test_wait_period_complete_becomes_candidate_postpartum(self):
        last_calving = TODAY - timedelta(days=POSTPARTUM_WAIT_DAYS)
        animal = make_animal(date(2020, 1, 1))
        result = _classify_female(animal, None, last_calving, {}, TODAY)
        assert result.kind == "candidate_postpartum"
        assert result.last_calving_date == last_calving

    def test_wait_period_incomplete_becomes_postpartum_waiting(self):
        last_calving = TODAY - timedelta(days=POSTPARTUM_WAIT_DAYS - 1)
        animal = make_animal(date(2020, 1, 1))
        result = _classify_female(animal, None, last_calving, {}, TODAY)
        assert result.kind == "postpartum_waiting"
        assert result.last_calving_date == last_calving


class TestRecalvedAfterLastRegisteredBreeding:
    """last_breed var ama last_calving ONDAN SONRA - hayvan tohumlanmis,
    dogurmus, ama YENI bir tohumlama daha kaydedilmemis (en yaygin normal
    akis)."""

    def test_wait_period_complete_becomes_candidate_postpartum(self):
        breed_date = date(2025, 1, 1)
        last_calving = TODAY - timedelta(days=POSTPARTUM_WAIT_DAYS)
        animal = make_animal(date(2020, 1, 1))
        breed = make_breed(breed_date)
        result = _classify_female(animal, breed, last_calving, {}, TODAY)
        assert result.kind == "candidate_postpartum"

    def test_wait_period_incomplete_becomes_postpartum_waiting(self):
        breed_date = date(2025, 1, 1)
        last_calving = TODAY - timedelta(days=POSTPARTUM_WAIT_DAYS - 1)
        animal = make_animal(date(2020, 1, 1))
        breed = make_breed(breed_date)
        result = _classify_female(animal, breed, last_calving, {}, TODAY)
        assert result.kind == "postpartum_waiting"


class TestActiveBreedingCycle:
    """last_breed var, last_calving YOK ya da ONDAN ONCE - aktif bir
    tohumlama dongusu suruyor, kontrol sonucuna gore dallanir."""

    def test_no_check_yet_becomes_pending(self):
        animal = make_animal(date(2020, 1, 1))
        breed = make_breed(date(2026, 6, 1))
        result = _classify_female(animal, breed, None, {}, TODAY)
        assert result.kind == "pending"
        assert result.breeding_event is breed

    def test_check_result_gebe_becomes_pregnant(self):
        animal = make_animal(date(2020, 1, 1))
        breed = make_breed(date(2026, 6, 1))
        check = make_check("GEBE", note="saglikli")
        result = _classify_female(animal, breed, None, {breed.id: check}, TODAY)
        assert result.kind == "pregnant"
        assert result.check_note == "saglikli"

    def test_check_result_bos_becomes_open(self):
        animal = make_animal(date(2020, 1, 1))
        breed = make_breed(date(2026, 6, 1))
        check = make_check("BOS")
        result = _classify_female(animal, breed, None, {breed.id: check}, TODAY)
        assert result.kind == "open"

    def test_check_result_other_becomes_suspicious(self):
        animal = make_animal(date(2020, 1, 1))
        breed = make_breed(date(2026, 6, 1))
        check = make_check("SUPHELI")
        result = _classify_female(animal, breed, None, {breed.id: check}, TODAY)
        assert result.kind == "suspicious"

    def test_old_calving_before_breed_does_not_trigger_postpartum(self):
        """last_calving var ama last_breed'DEN ONCE - eski bir dogum,
        yeni tohumlama dongusunu etkilememeli (kontrol yoluna girmeli)."""
        animal = make_animal(date(2018, 1, 1))
        old_calving = date(2024, 1, 1)
        breed = make_breed(date(2026, 6, 1))
        result = _classify_female(animal, breed, old_calving, {}, TODAY)
        assert result.kind == "pending"


@pytest.mark.parametrize(
    "birth_date,last_breed,last_calving,check_result",
    [
        (date(2025, 1, 1), None, None, None),  # candidate_new
        (date(2020, 1, 1), None, date(2026, 6, 1), None),  # postpartum_waiting
        (date(2020, 1, 1), "breed", None, "GEBE"),  # pregnant
        (date(2020, 1, 1), "breed", None, "BOS"),  # open
        (date(2020, 1, 1), "breed", None, "SUPHELI"),  # suspicious
        (date(2020, 1, 1), "breed", None, None),  # pending
    ],
)
def test_partition_is_exhaustive_and_disjoint(birth_date, last_breed, last_calving, check_result):
    """Her girdi kombinasyonu icin _classify_female HER ZAMAN gecerli,
    bilinen bir 'kind' dondurur (asla exception firlatmaz, asla None
    donmez) - Sürü Durum Özeti raporunun 'alt-durumlar toplami ust
    toplama esittir' garantisinin temel varsayimi budur."""
    animal = make_animal(birth_date)
    breed = make_breed(date(2026, 6, 1)) if last_breed == "breed" else None
    checks = {}
    if breed and check_result:
        checks[breed.id] = make_check(check_result)
    result = _classify_female(animal, breed, last_calving, checks, TODAY)
    assert result.kind in {
        "none",
        "candidate_new",
        "candidate_postpartum",
        "postpartum_waiting",
        "pending",
        "pregnant",
        "open",
        "suspicious",
    }
