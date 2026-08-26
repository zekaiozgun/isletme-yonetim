"""Genel amaçlı tablo -> PDF dönüştürücü.

Bu servis hiçbir raporun (breeding-candidates, herd-cost-summary, vb.)
içeriğini bilmez - sadece kendisine verilen başlık/açıklama/sütun/satır
verisini A4 sayfaya basar. Sütun genişlik sınıfları (narrow/wide) ve zebra
gölgelendirme, frontend'deki ekran içi ReportTable/print CSS mizanpajıyla
aynı görsel dili paylaşır (bkz. apps/web/src/components/ReportTable.tsx).

PDF, daha sonra referans alınabilmesi için başlık satırının sağına
oluşturulma tarih/saatini (Europe/Istanbul) basar - sunucunun kendi saat
dilimi (Render/Docker'da genelde UTC) ne olursa olsun kullanıcıya her
zaman yerel saat gösterilir.

Sütunlardan hiçbiri 'wide' (serbest metin/Not) değilse tablo sayfanın
tamamını kaplamaya ZORLANMAZ (table.full-width class'ı eklenmez) - aksi
halde tüm dar sütunlar eşit oranda gereksiz yere gerilip değerler
arasında çirkin boşluklar oluşur. Bu, ekran içi ReportTable'daki
`hasWideColumn` mantığıyla birebir aynıdır.

weasyprint import'u BİLEREK fonksiyon içinde yapılıyor: bu paket metin
şekillendirme için Pango/gobject'e (sistem kütüphanesi) ihtiyaç duyar -
Linux/Docker üzerinde (bkz. Dockerfile) sorunsuz çalışır ama yerel Windows
geliştirme ortamında bu kütüphaneler kurulu olmayabilir. Import'u modül
seviyesine değil fonksiyon içine almak, weasyprint hiç kullanılmadığı
sürece (örn. mapper/openapi doğrulama scriptleri) uygulamanın geri kalanının
yerel ortamda sorunsuz çalışmasını sağlar.
"""

import html
from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.modules.pdf_export.schemas import (
    AnimalProfilePdfRequest,
    PdfSimpleTable,
    PdfSummaryBox,
    PdfTableRequest,
    PdfWeightPoint,
)

_ISTANBUL = ZoneInfo("Europe/Istanbul")

_BASE_CSS = """
@page { size: A4; margin: 15mm 12mm; }
body { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 9pt; color: #1e293b; }
div.header-row { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
h1 { font-size: 14pt; margin: 0; color: #0f172a; }
span.generated-at { font-size: 8pt; color: #94a3b8; white-space: nowrap; }
p.description { font-size: 8pt; color: #64748b; margin: 4px 0 12px 0; }
table { border-collapse: collapse; }
table.full-width { width: 100%; }
thead th { background: #f8fafc; text-align: left; font-weight: 600; color: #475569;
  border-bottom: 1px solid #e2e8f0; padding: 4px 6px; }
tbody td { border-bottom: 1px solid #f1f5f9; padding: 4px 6px; vertical-align: top; }
tbody tr.even { background: #f8fafc; }
tbody tr.highlight td { background: #fffbeb; color: #78350f; font-weight: 600; }
td.narrow, th.narrow { white-space: nowrap; padding-left: 2px; padding-right: 2px; }
td.wide, th.wide { word-wrap: break-word; overflow-wrap: break-word; }
div.summary-boxes { display: flex; gap: 12px; margin: 8px 0 12px 0; }
div.summary-box { flex: 1; border: 1px solid #cbd5e1; background: #f1f5f9; border-radius: 4px;
  padding: 8px 12px; }
p.summary-label { font-size: 8pt; color: #64748b; margin: 0 0 2px 0; }
p.summary-value { font-size: 14pt; font-weight: 600; color: #0f172a; margin: 0; display: inline; }
span.summary-badge { font-size: 8.5pt; font-weight: 600; margin-left: 6px; padding: 1px 6px;
  border-radius: 999px; }
span.badge-positive { background: #ecfdf5; color: #047857; }
span.badge-negative { background: #fef2f2; color: #dc2626; }
p.summary-sublabel { font-size: 8pt; color: #94a3b8; margin: 2px 0 0 0; }
h2.section-title { font-size: 10pt; font-weight: 600; color: #64748b; text-transform: uppercase;
  letter-spacing: 0.03em; margin: 16px 0 6px 0; }
"""


def _summary_box_html(box: PdfSummaryBox) -> str:
    badge_html = ""
    if box.badge:
        badge_class = "badge-negative" if box.badge_negative else "badge-positive"
        badge_html = f'<span class="summary-badge {badge_class}">{_escape(box.badge)}</span>'
    sublabel_html = f'<p class="summary-sublabel">{_escape(box.sublabel)}</p>' if box.sublabel else ""
    return (
        '<div class="summary-box">'
        f'<p class="summary-label">{_escape(box.label)}</p>'
        f'<p class="summary-value">{_escape(box.value)}</p>'
        f"{badge_html}{sublabel_html}"
        "</div>"
    )


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _width_class(width: str | None) -> str:
    return width or ""


def render_table_pdf(data: PdfTableRequest) -> bytes:
    from weasyprint import HTML  # noqa: PLC0415 - bkz. modul docstring'i

    header_cells = "".join(
        f'<th class="{_width_class(col.width)}">{_escape(col.label)}</th>' for col in data.columns
    )

    highlighted = set(data.highlighted_rows)
    body_rows: list[str] = []
    for index, row in enumerate(data.rows):
        row_classes = ["highlight"] if index in highlighted else (["even"] if index % 2 == 1 else [])
        cells = "".join(
            f'<td class="{_width_class(col.width)}">{_escape(value)}</td>'
            for col, value in zip(data.columns, row, strict=False)
        )
        body_rows.append(f'<tr class="{" ".join(row_classes)}">{cells}</tr>')

    description_html = f'<p class="description">{_escape(data.description)}</p>' if data.description else ""
    summary_boxes_html = (
        f'<div class="summary-boxes">{"".join(_summary_box_html(box) for box in data.summary_boxes)}</div>'
        if data.summary_boxes
        else ""
    )
    generated_at = datetime.now(_ISTANBUL).strftime("%d/%m/%Y %H:%M")
    table_class = "full-width" if any(col.width == "wide" for col in data.columns) else ""

    html_doc = (
        "<html><head><meta charset=\"utf-8\" />"
        f"<style>{_BASE_CSS}</style></head><body>"
        '<div class="header-row">'
        f"<h1>{_escape(data.title)}</h1>"
        f'<span class="generated-at">Oluşturulma: {generated_at}</span>'
        "</div>"
        f"{description_html}"
        f"{summary_boxes_html}"
        f'<table class="{table_class}"><thead><tr>{header_cells}</tr></thead>'
        f"<tbody>{''.join(body_rows)}</tbody></table>"
        "</body></html>"
    )
    return HTML(string=html_doc).write_pdf()


def _format_number(value: float) -> str:
    """"12.00" -> "12", "12.30" -> "12.3" - kilo grafiginde nokta
    etiketleri icin (bkz. _format_percent_share, reports/service.py -
    ayni "gereksiz sifirlari temizle" deseni)."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _format_date_dmy(iso_date: str) -> str:
    try:
        return date.fromisoformat(iso_date[:10]).strftime("%d/%m/%Y")
    except ValueError:
        return iso_date


def _svg_weight_chart(points: list[PdfWeightPoint]) -> str:
    """components/TrendLineChart.tsx (ekran ici React bileseni) ile AYNI
    mizanpaj/mantik - tarihe gore ORANTILI x ekseni (olcumler esit
    araliklarla olmayabilir), her noktanin degeri dogrudan grafik
    uzerinde yazili. 2'den az nokta varsa bos string doner (cizilecek
    bir cizgi yoktur)."""
    if len(points) < 2:
        return ""
    width, height = 600, 170
    margin_top, margin_bottom, margin_x = 24, 20, 24
    plot_width = width - margin_x * 2
    plot_height = height - margin_top - margin_bottom

    ordinals = [date.fromisoformat(p.date[:10]).toordinal() for p in points]
    min_ord, max_ord = min(ordinals), max(ordinals)
    date_span = (max_ord - min_ord) or 1

    values = [p.value for p in points]
    min_v, max_v = min(values), max(values)
    padding = (max_v - min_v) * 0.2 or abs(max_v) * 0.1 or 1
    y_min, y_max = min_v - padding, max_v + padding
    y_span = (y_max - y_min) or 1

    def x_for(ordinal: int) -> float:
        return margin_x + ((ordinal - min_ord) / date_span) * plot_width

    def y_for(value: float) -> float:
        return margin_top + plot_height - ((value - y_min) / y_span) * plot_height

    coords = [(x_for(o), y_for(p.value)) for o, p in zip(ordinals, points, strict=True)]
    path_d = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(coords))

    dots: list[str] = []
    for i, ((cx, cy), p) in enumerate(zip(coords, points, strict=True)):
        anchor = "start" if i == 0 else ("end" if i == len(points) - 1 else "middle")
        label_y = (cy - 8) if (cy - margin_top) > 12 else (cy + 15)
        dots.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.5" fill="#0f172a" />'
            f'<text x="{cx:.1f}" y="{label_y:.1f}" font-size="10" font-weight="600" '
            f'fill="#0f172a" text-anchor="{anchor}">{_escape(_format_number(p.value))}</text>'
        )

    baseline_y = margin_top + plot_height
    return (
        f'<svg viewBox="0 0 {width} {height}" style="width:100%">'
        f'<line x1="{margin_x}" y1="{baseline_y}" x2="{width - margin_x}" y2="{baseline_y}" '
        'stroke="#e2e8f0" stroke-width="1" />'
        f'<path d="{path_d}" fill="none" stroke="#0f172a" stroke-width="2" />'
        f"{''.join(dots)}"
        f'<text x="{margin_x}" y="{height - 4}" font-size="11" fill="#94a3b8">'
        f"{_escape(_format_date_dmy(points[0].date))}</text>"
        f'<text x="{width - margin_x}" y="{height - 4}" font-size="11" fill="#94a3b8" text-anchor="end">'
        f"{_escape(_format_date_dmy(points[-1].date))}</text>"
        "</svg>"
    )


def _simple_table_html(table: PdfSimpleTable) -> str:
    header_cells = "".join(f"<th>{_escape(col)}</th>" for col in table.columns)
    body_rows: list[str] = []
    for index, row in enumerate(table.rows):
        row_class = "even" if index % 2 == 1 else ""
        cells = "".join(f"<td>{_escape(value)}</td>" for value in row)
        body_rows.append(f'<tr class="{row_class}">{cells}</tr>')
    if not body_rows:
        colspan = max(len(table.columns), 1)
        body_rows.append(f'<tr><td colspan="{colspan}" style="color:#94a3b8;">Kayıt yok.</td></tr>')
    return (
        f'<h2 class="section-title">{_escape(table.title)}</h2>'
        f'<table class="full-width"><thead><tr>{header_cells}</tr></thead>'
        f"<tbody>{''.join(body_rows)}</tbody></table>"
    )


def render_animal_profile_pdf(data: AnimalProfilePdfRequest) -> bytes:
    """Tek bir hayvanin TAM profilini (kimlik + degerleme + genetik + soy
    kutugu + kilo trendi + saglik/ureme/padok/degerlendirme gecmisi) tek
    bir A4 belgesinde toplar - render_table_pdf ile AYNI temel CSS/sayfa
    ayarlarini paylasir, ama tek tablo yerine COK BOLUMLU bir belge
    yapisi kurar (bkz. apps/web animal profile sayfasiyla ayni bolum
    sirasi: Genetik Karma -> Soy Kutugu -> Kilo Trendi -> Saglik/Ureme/
    Padok/Degerlendirme)."""
    from weasyprint import HTML  # noqa: PLC0415 - bkz. modul docstring'i

    generated_at = datetime.now(_ISTANBUL).strftime("%d/%m/%Y %H:%M")

    info_boxes_html = (
        f'<div class="summary-boxes">{"".join(_summary_box_html(box) for box in data.info_boxes)}</div>'
        if data.info_boxes
        else ""
    )
    genetic_html = (
        f'<p class="description"><strong>Genetik Karma:</strong> {_escape(data.genetic_composition)}</p>'
        if data.genetic_composition
        else ""
    )
    pedigree_html = (
        _simple_table_html(data.pedigree_table) if data.pedigree_table and data.pedigree_table.rows else ""
    )
    chart_svg = _svg_weight_chart(data.weight_points)
    chart_html = f'<h2 class="section-title">Kilo Trend Grafiği</h2>{chart_svg}' if chart_svg else ""
    tables_html = "".join(_simple_table_html(t) for t in data.tables)

    html_doc = (
        "<html><head><meta charset=\"utf-8\" />"
        f"<style>{_BASE_CSS}</style></head><body>"
        '<div class="header-row">'
        f"<h1>{_escape(data.title)}</h1>"
        f'<span class="generated-at">Oluşturulma: {generated_at}</span>'
        "</div>"
        f'<p class="description">{_escape(data.subtitle)}<br/>{_escape(data.meta_line)}</p>'
        f"{genetic_html}"
        f"{info_boxes_html}"
        f"{pedigree_html}"
        f"{chart_html}"
        f"{tables_html}"
        "</body></html>"
    )
    return HTML(string=html_doc).write_pdf()
