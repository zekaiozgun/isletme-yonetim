from typing import Literal

from pydantic import BaseModel


class PdfColumnSpec(BaseModel):
    label: str
    # ReportColumn['width'] ile ayni anlam (bkz. apps/web/src/lib/reports.ts) -
    # 'narrow' dar sutunlar, 'wide' serbest metin sutunlari (PDF'te - ekrandaki
    # "..." ile kesmenin aksine - satir kaydirilir, cunku basili kagitta
    # "uzerine gel" diye bir etkilesim yoktur; hicbir veri kaybolmamali).
    width: Literal["narrow", "wide"] | None = None


class PdfSummaryBox(BaseModel):
    """Basliğin altinda, tablodan once gosterilen vurgulu bir ozet kutusu
    (orn. 'Toplam Edinme Degeri' / 'Toplam Tahmini Piyasa Degeri') - ekran
    ici HerdAnimalValueTable.tsx ile ayni bilgiyi tasir, PDF'e ozel yeniden
    hesaplama YAPILMAZ, deger zaten formatlanmis metin olarak gelir."""

    label: str
    value: str
    sublabel: str | None = None
    # Orn. "+%26,5" - renk (kirmizi/yesil) badge_negative'e gore secilir,
    # metinden parse edilmeye CALISILMAZ (kirilgan olurdu).
    badge: str | None = None
    badge_negative: bool = False


class PdfTableRequest(BaseModel):
    title: str
    description: str | None = None
    summary_boxes: list[PdfSummaryBox] = []
    columns: list[PdfColumnSpec]
    rows: list[list[str]]
    # Vurgulanacak (rowHighlight=true olan) satirlarin 0-tabanli indeksleri.
    highlighted_rows: list[int] = []
