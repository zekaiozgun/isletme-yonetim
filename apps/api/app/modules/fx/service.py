"""TCMB gunluk kur XML servisinden USD/TRY satis kuru cekip onbellekler.

Anayasa m.4/m.5: bu bir "hesaplama" degil dis kaynakli bir fact'in
onbelleklenmesidir - raporlar bunu kullanarak TL tutarlarin USD
karsiligini ISTEK ANINDA turetir, hicbir maliyet tablosuna kur yazilmaz.
"""

import logging
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.fx.models import ExchangeRate

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


def get_usd_try_rate(db: Session, on_date: date) -> Decimal | None:
    """Verilen tarih icin USD/TRY satis kurunu dondurur - once onbellekten,
    yoksa TCMB'den cekip onbellege yazar. Hafta sonu/tatil gibi bulten
    olmayan tarihlerde en yakin ONCEKI is gunune duser (bulunan kur hem
    o gercek tarih hem orijinal istenen tarih icin onbelleklenir). Kur hic
    bulunamazsa (ag hatasi + onbellek bos) None doner - cagiran taraf bunu
    "—" olarak gostermeli, hata firlatilmaz."""
    cached = db.get(ExchangeRate, on_date)
    if cached is not None:
        return cached.usd_try_selling

    for offset in range(MAX_LOOKBACK_DAYS + 1):
        candidate_date = on_date - timedelta(days=offset)

        if offset > 0:
            candidate_cached = db.get(ExchangeRate, candidate_date)
            if candidate_cached is not None:
                _cache_rate(db, on_date, candidate_cached.usd_try_selling)
                return candidate_cached.usd_try_selling

        rate = _fetch_usd_selling_from_tcmb(candidate_date)
        if rate is not None:
            _cache_rate(db, candidate_date, rate)
            if candidate_date != on_date:
                _cache_rate(db, on_date, rate)
            return rate

    logger.warning("TCMB kuru bulunamadi: %s (ve %s gun geriye kadar)", on_date, MAX_LOOKBACK_DAYS)
    return None
