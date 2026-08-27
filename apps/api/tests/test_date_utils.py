"""core/date_utils.remaining_days_after_months icin birim testleri -
"N ay M gun" karma yas gosteriminin dayandigi hesaplama. DB gerekmez."""

from datetime import date

from app.core.date_utils import full_months_between, remaining_days_after_months


def test_remaining_days_after_months_exact_month_boundary_is_zero():
    assert remaining_days_after_months(date(2026, 1, 15), date(2026, 5, 15), 4) == 0


def test_remaining_days_after_months_mid_month():
    # 2026-01-15 -> 4 tam ay = 2026-05-15, 2026-06-01'e kadar 17 gun kaldi.
    assert remaining_days_after_months(date(2026, 1, 15), date(2026, 6, 1), 4) == 17


def test_remaining_days_after_months_matches_full_months_between_for_variable_month_lengths():
    # Subat (28 gun) ile Temmuz (31 gun) arasi - sabit "30 gun = 1 ay"
    # varsayimi burada yanlis sonuc verirdi (bkz. Buz-4440-Prolap).
    start = date(2026, 1, 31)
    end = date(2026, 3, 3)
    months = full_months_between(start, end)
    assert months == 1
    assert remaining_days_after_months(start, end, months) == 3


def test_remaining_days_after_months_returns_zero_when_end_before_start():
    assert remaining_days_after_months(date(2026, 5, 1), date(2026, 1, 1), 0) == 0
