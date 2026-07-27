"""Genel amaçlı tablo -> PDF dönüştürücü.

Bu servis hiçbir raporun (breeding-candidates, herd-cost-summary, vb.)
içeriğini bilmez - sadece kendisine verilen başlık/açıklama/sütun/satır
verisini A4 sayfaya basar. Sütun genişlik sınıfları (narrow/wide) ve zebra
gölgelendirme, frontend'deki ekran içi ReportTable/print CSS mizanpajıyla
aynı görsel dili paylaşır (bkz. apps/web/src/components/ReportTable.tsx).

weasyprint import'u BİLEREK fonksiyon içinde yapılıyor: bu paket metin
şekillendirme için Pango/gobject'e (sistem kütüphanesi) ihtiyaç duyar -
Linux/Docker üzerinde (bkz. Dockerfile) sorunsuz çalışır ama yerel Windows
geliştirme ortamında bu kütüphaneler kurulu olmayabilir. Import'u modül
seviyesine değil fonksiyon içine almak, weasyprint hiç kullanılmadığı
sürece (örn. mapper/openapi doğrulama scriptleri) uygulamanın geri kalanının
yerel ortamda sorunsuz çalışmasını sağlar.
"""

import html

from app.modules.pdf_export.schemas import PdfTableRequest

_BASE_CSS = """
@page { size: A4; margin: 15mm 12mm; }
body { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 9pt; color: #1e293b; }
h1 { font-size: 14pt; margin: 0 0 4px 0; color: #0f172a; }
p.description { font-size: 8pt; color: #64748b; margin: 0 0 12px 0; }
table { width: 100%; border-collapse: collapse; }
thead th { background: #f8fafc; text-align: left; font-weight: 600; color: #475569;
  border-bottom: 1px solid #e2e8f0; padding: 4px 6px; }
tbody td { border-bottom: 1px solid #f1f5f9; padding: 4px 6px; vertical-align: top; }
tbody tr.even { background: #f8fafc; }
tbody tr.highlight td { background: #fffbeb; color: #78350f; font-weight: 600; }
td.narrow, th.narrow { white-space: nowrap; padding-left: 2px; padding-right: 2px; }
td.wide, th.wide { word-wrap: break-word; overflow-wrap: break-word; }
"""


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

    html_doc = (
        "<html><head><meta charset=\"utf-8\" />"
        f"<style>{_BASE_CSS}</style></head><body>"
        f"<h1>{_escape(data.title)}</h1>"
        f"{description_html}"
        f"<table><thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody></table>"
        "</body></html>"
    )
    return HTML(string=html_doc).write_pdf()
