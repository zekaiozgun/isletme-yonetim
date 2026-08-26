"""Hayvan Profili PDF'inin saf yardimci fonksiyonlari icin birim
testleri (app/modules/pdf_export/service.py) - weasyprint/DB GEREKMEZ,
sadece _svg_weight_chart/_simple_table_html/_format_* string/matematik
uretiyor, tamamen izole calisir."""

from app.modules.pdf_export.schemas import PdfSimpleTable, PdfWeightPoint
from app.modules.pdf_export.service import (
    _format_date_dmy,
    _format_number,
    _simple_table_html,
    _svg_weight_chart,
)


def test_format_number_strips_trailing_zeros():
    assert _format_number(12.0) == "12"
    assert _format_number(12.30) == "12.3"
    assert _format_number(0.0) == "0"


def test_format_date_dmy_converts_iso_to_turkish_format():
    assert _format_date_dmy("2026-01-15") == "15/01/2026"


def test_format_date_dmy_falls_back_to_raw_on_bad_input():
    assert _format_date_dmy("not-a-date") == "not-a-date"


def test_svg_chart_empty_for_fewer_than_two_points():
    assert _svg_weight_chart([]) == ""
    assert _svg_weight_chart([PdfWeightPoint(date="2026-01-01", value=100)]) == ""


def test_svg_chart_renders_valid_svg_with_two_points():
    points = [
        PdfWeightPoint(date="2026-01-01", value=100),
        PdfWeightPoint(date="2026-02-01", value=150),
    ]
    svg = _svg_weight_chart(points)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "100" in svg
    assert "150" in svg
    assert "01/01/2026" in svg
    assert "01/02/2026" in svg


def test_svg_chart_handles_identical_dates_without_crashing():
    points = [
        PdfWeightPoint(date="2026-01-01", value=100),
        PdfWeightPoint(date="2026-01-01", value=110),
    ]
    svg = _svg_weight_chart(points)
    assert svg.startswith("<svg")


def test_svg_chart_handles_identical_values_without_crashing():
    points = [
        PdfWeightPoint(date="2026-01-01", value=100),
        PdfWeightPoint(date="2026-02-01", value=100),
    ]
    svg = _svg_weight_chart(points)
    assert svg.startswith("<svg")


def test_simple_table_html_renders_rows():
    table = PdfSimpleTable(title="Sağlık Geçmişi", columns=["Tarih", "Olay"], rows=[["15/01/2026", "Aşı"]])
    result = _simple_table_html(table)
    assert "Sağlık Geçmişi" in result
    assert "<th>Tarih</th>" in result
    assert "<td>Aşı</td>" in result


def test_simple_table_html_shows_placeholder_for_empty_rows():
    table = PdfSimpleTable(title="Sağlık Geçmişi", columns=["Tarih"], rows=[])
    result = _simple_table_html(table)
    assert "Kayıt yok." in result


def test_simple_table_html_escapes_html_in_cell_values():
    table = PdfSimpleTable(title="Not", columns=["Metin"], rows=[["<script>alert(1)</script>"]])
    result = _simple_table_html(table)
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
