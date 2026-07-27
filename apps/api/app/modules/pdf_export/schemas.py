from typing import Literal

from pydantic import BaseModel


class PdfColumnSpec(BaseModel):
    label: str
    # ReportColumn['width'] ile ayni anlam (bkz. apps/web/src/lib/reports.ts) -
    # 'narrow' dar sutunlar, 'wide' serbest metin sutunlari (PDF'te - ekrandaki
    # "..." ile kesmenin aksine - satir kaydirilir, cunku basili kagitta
    # "uzerine gel" diye bir etkilesim yoktur; hicbir veri kaybolmamali).
    width: Literal["narrow", "wide"] | None = None


class PdfTableRequest(BaseModel):
    title: str
    description: str | None = None
    columns: list[PdfColumnSpec]
    rows: list[list[str]]
    # Vurgulanacak (rowHighlight=true olan) satirlarin 0-tabanli indeksleri.
    highlighted_rows: list[int] = []
