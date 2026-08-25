"""_blend_feed_moving_average icin birim testleri
(app/modules/reports/service.py).

Bu fonksiyon HICBIR DB sorgusu yapmaz (butun parametreler hazir Python
degerleridir) - bu yuzden test icin veritabani/fixture gerekmez, tamamen
izole calisir. Asil amac: onceki ("tum-zamanlarin toplami") yontemin
TUKENMIS eski alimlari sonsuza kadar ortalamaya dahil etme hatasini,
yeni (hareketli/perpetual) yontemin gercekten duzelttigini dogrulamak.
"""

from datetime import date
from decimal import Decimal

from app.modules.reports.service import _blend_feed_moving_average

D = Decimal


def test_no_purchases_returns_none():
    assert _blend_feed_moving_average([], []) is None


def test_single_purchase_uses_its_own_unit_cost():
    purchases = [(date(2026, 1, 1), D("1000"), D("10000"))]  # 1000kg @ 10 TL/kg
    assert _blend_feed_moving_average(purchases, [D("0")]) == D("10")


def test_two_purchases_zero_consumption_blends_by_weight():
    # 1000kg @ 10 TL/kg, sonra (hic tuketim olmadan) +500kg @ 20 TL/kg
    purchases = [
        (date(2026, 1, 1), D("1000"), D("10000")),
        (date(2026, 2, 1), D("500"), D("10000")),
    ]
    result = _blend_feed_moving_average(purchases, [D("0"), D("0")])
    # (1000*10 + 500*20) / 1500 = 20000/1500 = 13.3333...
    assert result == (D("1000") * D("10") + D("500") * D("20")) / D("1500")


def test_full_depletion_between_purchases_resets_average_to_new_price():
    """Kullanicinin tam olarak isaret ettigi senaryo: eski (ucuz) alim
    TAMAMEN tuketildikten sonra yeni bir alim geldiginde, ortalama eski
    fiyatla KARISMAMALI - dogrudan yeni alimin kendi fiyati olmali."""
    purchases = [
        (date(2026, 1, 1), D("1000"), D("10000")),  # 10 TL/kg
        (date(2026, 8, 1), D("500"), D("10000")),  # 20 TL/kg
    ]
    # Iki alim arasinda TAM 1000kg tuketildi (stok sifira dustu).
    result = _blend_feed_moving_average(purchases, [D("0"), D("1000")])
    assert result == D("20")


def test_partial_depletion_blends_remaining_stock_with_new_purchase():
    purchases = [
        (date(2026, 1, 1), D("1000"), D("10000")),  # 10 TL/kg
        (date(2026, 8, 1), D("500"), D("10000")),  # 20 TL/kg
    ]
    # 400kg tuketildi, 600kg stokta kaldi (hala 10 TL/kg'dan).
    result = _blend_feed_moving_average(purchases, [D("0"), D("400")])
    # (600*10 + 500*20) / 1100
    assert result == (D("600") * D("10") + D("500") * D("20")) / D("1100")


def test_over_consumption_clamps_to_zero_not_negative():
    """Tuketim, o ana kadarki toplam alimdan FAZLA girilmisse (gec girilen
    alim/kotu veri) stok sifirda kilitlenir - eksiye dusmez, yeni alim
    yine kendi fiyatiyla basa doner."""
    purchases = [
        (date(2026, 1, 1), D("1000"), D("10000")),  # 10 TL/kg
        (date(2026, 8, 1), D("500"), D("10000")),  # 20 TL/kg
    ]
    # 1500kg tuketildi denildi ama sadece 1000kg vardi.
    result = _blend_feed_moving_average(purchases, [D("0"), D("1500")])
    assert result == D("20")


def test_three_purchases_chain_sequentially():
    purchases = [
        (date(2026, 1, 1), D("1000"), D("10000")),  # 10 TL/kg
        (date(2026, 3, 1), D("1000"), D("10000")),  # sifir tuketimle: (1000*10+1000*10)/2000 = 10
        (date(2026, 8, 1), D("1000"), D("30000")),  # tam tuketimle (2000kg): dogrudan 30 TL/kg
    ]
    result = _blend_feed_moving_average(purchases, [D("0"), D("0"), D("2000")])
    assert result == D("30")


def test_zero_kg_purchase_does_not_crash():
    purchases = [(date(2026, 1, 1), D("0"), D("0"))]
    assert _blend_feed_moving_average(purchases, [D("0")]) == D("0")
