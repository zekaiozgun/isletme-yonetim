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


class PdfWeightPoint(BaseModel):
    """Kilo Trend grafiginin TEK bir noktasi - date ISO formatinda (grafik
    x-eksenini tarihe GORE ORANTILI kurmak icin, bkz.
    components/TrendLineChart.tsx ile ayni mantik), value kg cinsinden."""

    date: str
    value: float


class PdfSimpleTable(BaseModel):
    """Hayvan Profili PDF'indeki kucuk alt tablolardan biri (orn. Saglik
    Gecmisi) - baslik + sutun basliklari + satirlar, PdfTableRequest'in
    kucultulmus hali (ozet kutusu/vurgu yok)."""

    title: str
    columns: list[str]
    rows: list[list[str]]


class AnimalProfilePdfRequest(BaseModel):
    """Tek bir hayvanin TAM profilini (kimlik + degerleme + genetik +
    soy kutugu + kilo trendi + saglik/ureme/padok/degerlendirme gecmisi)
    tek bir PDF belgesinde toplar - HerdAnimalValueTable.tsx'teki
    ozet-kutusu deseniyle AYNI felsefe: butun degerler zaten frontend'de
    formatlanmis metin olarak gelir, PDF tarafinda yeniden hesaplama
    YAPILMAZ (istisna: kilo grafiginin kendisi, gercek sayisal
    koordinatlar gerektirir, bkz. weight_points)."""

    title: str
    subtitle: str
    meta_line: str
    genetic_composition: str | None = None
    info_boxes: list[PdfSummaryBox] = []
    pedigree_table: PdfSimpleTable | None = None
    weight_points: list[PdfWeightPoint] = []
    tables: list[PdfSimpleTable] = []
