"""Anayasa m.5: yasla ilgili hesaplamalar (age_months vb.) hicbir yerde
saklanmaz, istek aninda buradaki paylasilan mantikla turetilir."""

import calendar
from datetime import date


def full_months_between(start: date, end: date) -> int:
    """iki tarih arasindaki TAM (takvim) ay sayisi. dateutil'e gerek yok."""
    if end < start:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return max(months, 0)


def add_months(start: date, months: int) -> date:
    """start tarihine months ay ekler (takvim ay aritmetigi). Gun, hedef
    ayda tasarsa (orn. 31 Ocak + 1 ay) o ayin son gunune sabitlenir."""
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def remaining_days_after_months(start: date, end: date, months: int) -> int:
    """full_months_between(start, end) == months TAM ay dusuldukten
    SONRA kalan gun sayisi - "N ay M gun" gibi karma bir yas gosterimi
    icin. add_months ile AYNI takvim-ay tanimini kullanir, boylece ay+gun
    toplami her zaman end tarihine tam oturur (28-31 gunluk ay uzunluk
    farkliliklarindan kaynaklanan belirsizlik olusmaz - bkz. Buz-4440-
    Prolap: sabit "30 gun = 1 ay" varsayimi yanlis sonuc vermisti)."""
    if end < start:
        return 0
    return (end - add_months(start, months)).days
