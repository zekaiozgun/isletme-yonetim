"""Anayasa m.5: yasla ilgili hesaplamalar (age_months vb.) hicbir yerde
saklanmaz, istek aninda buradaki paylasilan mantikla turetilir."""

from datetime import date


def full_months_between(start: date, end: date) -> int:
    """iki tarih arasindaki TAM (takvim) ay sayisi. dateutil'e gerek yok."""
    if end < start:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return max(months, 0)
