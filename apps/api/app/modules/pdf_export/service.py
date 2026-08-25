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
from datetime import datetime
from zoneinfo import ZoneInfo

from app.modules.pdf_export.schemas import PdfSummaryBox, PdfTableRequest

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
