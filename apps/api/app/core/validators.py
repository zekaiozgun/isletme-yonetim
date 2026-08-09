"""Veri girisinde kronolojik olarak imkansiz tarih siralamalarini
(orn. olum tarihinin dogum tarihinden once olmasi) engelleyen paylasilan
dogrulama yardimcisi. Servis katmani, ilgili create/update fonksiyonlarinda
DB yazisindan once cagirir; ihlal DomainError olarak firlatilir (bkz.
app/main.py - router bunu 422'ye cevirir)."""

from datetime import date

from app.core.exceptions import DomainError


def require_date_order(early_date: date | None, early_label: str, late_date: date | None, late_label: str) -> None:
    """early_date, late_date'ten SONRA olamaz (esitlik serbest). Taraflardan
    biri None ise (opsiyonel/henuz bilinmeyen tarih) sessizce gecer - eksik
    veri ayri bir dogrulamanin (schema-level required/optional) konusu."""
    if early_date is None or late_date is None:
        return
    if early_date > late_date:
        raise DomainError(
            f"{early_label} ({early_date.isoformat()}), {late_label} tarihinden "
            f"({late_date.isoformat()}) sonra olamaz."
        )
