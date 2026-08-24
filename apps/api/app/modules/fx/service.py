"""TCMB gunluk kur XML servisinden USD/TRY satis kuru cekip onbellekler.

Anayasa m.4/m.5: bu bir "hesaplama" degil dis kaynakli bir fact'in
onbelleklenmesidir - raporlar bunu kullanarak TL tutarlarin USD
karsiligini ISTEK ANINDA turetir, hicbir maliyet tablosuna kur yazilmaz.
"""

import logging
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.animal.models import Animal
from app.modules.death.models import Death
from app.modules.fx.models import ExchangeRate
from app.modules.health.models import HealthEvent
from app.modules.sale.models import Sale

logger = logging.getLogger(__name__)

TCMB_ARCHIVE_URL = "https://www.tcmb.gov.tr/kurlar/{yyyymm}/{ddmmyyyy}.xml"
FETCH_TIMEOUT_SECONDS = 3
MAX_LOOKBACK_DAYS = 10


def _fetch_usd_selling_from_tcmb(on_date: date) -> Decimal | None:
    """Verilen tarih icin TCMB bulteninden USD ForexSelling degerini ceker.
    Bulten yoksa (hafta sonu/tatil) veya ag hatasi olursa None doner -
    hicbir durumda exception disariya sizdirilmaz (rapor akisi dis
    servise bagimli kalmamali)."""
    url = TCMB_ARCHIVE_URL.format(yyyymm=on_date.strftime("%Y%m"), ddmmyyyy=on_date.strftime("%d%m%Y"))
    try:
        with urllib.request.urlopen(url, timeout=FETCH_TIMEOUT_SECONDS) as response:  # noqa: S310 - sabit TCMB host
            body = response.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None

    try:
        root = ET.fromstring(body)  # noqa: S314 - TCMB'nin kendi sabit XML servisi, kullanici girdisi degil
        usd = root.find("./Currency[@Kod='USD']/ForexSelling")
        if usd is None or not usd.text:
            return None
        return Decimal(usd.text)
    except (ET.ParseError, InvalidOperation):
        return None


def _cache_rate(db: Session, rate_date: date, usd_try_selling: Decimal) -> None:
    if db.get(ExchangeRate, rate_date) is not None:
        return
    db.add(ExchangeRate(rate_date=rate_date, usd_try_selling=usd_try_selling))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def _read_cached_rate_with_fallback(db: Session, on_date: date) -> tuple[Decimal, date] | None:
    """on_date'in kendisi ya da MAX_LOOKBACK_DAYS icindeki en yakin onceki
    is gunu ONBELLEKTE varsa (kur, bulundugu_tarih) doner - SAF OKUMA,
    hicbir ag istegi ya da DB YAZISI yapmaz (bkz. get_cached_usd_try_rate
    docstring'i - raporlama katmaninin gercekten sifir yan etkili olmasi
    icin onbellege-yazma optimizasyonu BURADA DEGIL, sadece get_usd_try_rate
    icinde yapilir)."""
    for offset in range(MAX_LOOKBACK_DAYS + 1):
        candidate_date = on_date - timedelta(days=offset)
        cached = db.get(ExchangeRate, candidate_date)
        if cached is not None:
            return cached.usd_try_selling, candidate_date
    return None


def get_cached_usd_try_rate(db: Session, on_date: date) -> Decimal | None:
    """Raporlarin kullanmasi gereken SALT-OKUNUR versiyon: hicbir ag
    istegi ATMAZ ve hicbir DB YAZISI YAPMAZ (get_usd_try_rate'in aksine,
    bulunan bir onceki is gunu kurunu on_date icin ayrica onbeklemez) -
    sadece onbellegi (+ en yakin onceki is gununu) okur, bulunamazsa
    ANINDA None doner (cagiran taraf "—" gostermeli).

    Bunun nedeni: bir rapor (orn. Suru Kar/Zarar) araliktaki DUZINELERCE
    farkli tarih icin (her satis/olum/saglik olayi) kur sorabilir - eger
    her biri onbellekte yoksa TCMB'ye tek tek senkron istek atsaydi
    (bkz. get_usd_try_rate), toplam sure dakikalarca surup istegin zaman
    asimina ugramasina, kullaniciya "veri bulunamadi" gibi yaniltici bos
    bir sonuc donmesine yol acabilirdi (Anayasa m.2: raporlama dis
    servise bagimli/YAVAS olmamali VE herhangi bir DB yazisi yapmamalidir).
    Canli kur cekme islemi bunun yerine veri girisi aninda (bkz.
    sale/death/health_event servisleri) ve gunluk isitma isinde (bkz.
    app/main.py: GET /fx/warm-cache) yapilir."""
    result = _read_cached_rate_with_fallback(db, on_date)
    return result[0] if result is not None else None


def get_usd_try_rate(db: Session, on_date: date) -> Decimal | None:
    """Verilen tarih icin USD/TRY satis kurunu dondurur - once onbellekten
    (+ en yakin onceki is gunu), yoksa TCMB'den CANLI cekip onbellege
    yazar. Hafta sonu/tatil gibi bulten olmayan tarihlerde en yakin ONCEKI
    is gunune duser. Kur hic bulunamazsa (ag hatasi + onbellek bos) None
    doner - cagiran taraf bunu "—" olarak gostermeli, hata firlatilmaz.

    Bu fonksiyon YAVAS OLABILIR (ag cagrisi icerir) - bu yuzden SADECE tek
    bir tarihin soz konusu oldugu veri girisi anlarinda (bir Satis/Olum/
    Saglik Olayi kaydedilirken o tarihin kuru onbellege isitilir) ve
    gunluk isitma isinde kullanilir. Raporlar bunun yerine
    get_cached_usd_try_rate'i kullanmalidir - ASLA bunu dogrudan
    cagirmamalidir (duzinelerce tarih icin sirayla canli istek atip
    zaman asimina ugrayabilir)."""
    cached = _read_cached_rate_with_fallback(db, on_date)
    if cached is not None:
        rate, found_date = cached
        if found_date != on_date:
            _cache_rate(db, on_date, rate)
        return rate

    for offset in range(MAX_LOOKBACK_DAYS + 1):
        candidate_date = on_date - timedelta(days=offset)
        rate = _fetch_usd_selling_from_tcmb(candidate_date)
        if rate is not None:
            _cache_rate(db, candidate_date, rate)
            if candidate_date != on_date:
                _cache_rate(db, on_date, rate)
            return rate

    logger.warning("TCMB kuru bulunamadi: %s (ve %s gun geriye kadar)", on_date, MAX_LOOKBACK_DAYS)
    return None


def warm_rate_on_entry(db: Session, on_date: date) -> None:
    """Sale/Death/HealthEvent/Animal servisleri, kendi asil kaydini commit
    ETTIKTEN SONRA bu fonksiyonu cagirir - o tarihin kurunu onbellege
    isitmek YAN ISTIR, asil islemin basarisi buna BAGLI DEGILDIR. Bu
    yuzden get_usd_try_rate'in aksine HICBIR ISTISNAYI DISARIYA SIZDIRMAZ:
    TCMB agi/DB gibi beklenmedik bir hata olursa asil kayit (zaten
    commit edilmis) etkilenmeden sadece loglanir - kullaniciya, basariyla
    kaydedilmis bir Satis/Olum/... icin yanlislikla 500 hatasi donmez.
    Isitilemeyen tarih, bir sonraki gunluk warm_cache calistirmasinda
    (bkz. warm_cache) zaten tekrar denenir."""
    try:
        get_usd_try_rate(db, on_date)
    except Exception:
        logger.warning("Kur isitma basarisiz oldu (asil kayit etkilenmedi): %s", on_date, exc_info=True)


WARM_CACHE_TIME_BUDGET_SECONDS = 20.0


def warm_cache(db: Session, time_budget_seconds: float = WARM_CACHE_TIME_BUDGET_SECONDS) -> dict[str, float | int]:
    """Gunluk isitma isi (bkz. app/main.py: GET /fx/warm-cache + GitHub
    Actions is akisi 'fx-rate-warmup.yml'): once 'dun'un (TCMB bulteni yayinlanmis
    olmasi beklenen en son is gunu) kurunu isitir; ardindan Sale/Death/
    HealthEvent(maliyetli)/Animal(giris degeri girilmis) tablolarindaki,
    ONBELLEKTE henuz olmayan tarihleri (en yeniden eskiye) tarayip isitir -
    bu ozellikten ONCE girilmis kayitlari kademeli olarak geriye doner
    doldurur (veri girisi aninda isitma, bkz. sale/death/health_event/
    animal servisleri, SADECE BUNDAN SONRAKI kayitlari kapsar).

    Tek bir calistirmanin ASLA cok uzun surmemesi icin (bkz. Suru Kar/Zarar
    raporundaki orijinal zaman asimi sorunu - raporlar artik onbellek-
    salt-okunur oldugu icin bu fonksiyon YAVAS olsa bile raporlari
    ETKILEMEZ, ama yine de sinirsiz surmemesi icin) time_budget_seconds
    asilinca durur - kalan tarihler bir sonraki gunluk calistirmada
    isitilir (kalici degil, kademeli/self-healing bir yaklasim)."""
    start_time = time.monotonic()
    warmed = 0
    already_cached = 0
    hit_time_budget = False

    yesterday = date.today() - timedelta(days=1)
    if db.get(ExchangeRate, yesterday) is not None:
        already_cached += 1
    else:
        get_usd_try_rate(db, yesterday)
        warmed += 1

    dates: set[date] = set()
    dates.update(db.scalars(select(Sale.sale_date)).all())
    dates.update(db.scalars(select(Death.death_date)).all())
    dates.update(db.scalars(select(HealthEvent.event_date).where(HealthEvent.cost.isnot(None))).all())
    dates.update(db.scalars(select(Animal.entry_date).where(Animal.entry_value.isnot(None))).all())

    for on_date in sorted(dates, reverse=True):
        if time.monotonic() - start_time > time_budget_seconds:
            hit_time_budget = True
            break
        if db.get(ExchangeRate, on_date) is not None:
            already_cached += 1
            continue
        get_usd_try_rate(db, on_date)
        warmed += 1

    return {
        "warmed": warmed,
        "already_cached": already_cached,
        "remaining_dates": len(dates) + 1 - warmed - already_cached,
        "hit_time_budget": hit_time_budget,
        "elapsed_seconds": round(time.monotonic() - start_time, 2),
    }
