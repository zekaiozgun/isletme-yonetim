import type { ApiRecord } from './api';

export interface ReportColumn {
  key: string;
  label: string;
  format?: (value: unknown, row: ApiRecord) => string;
}

export interface ReportConfig {
  slug: string;
  title: string;
  description: string;
  endpoint: string;
  columns: ReportColumn[];
  /** true dönerse satır dikkat çekecek şekilde vurgulanır (örn. gecikmiş gebelik kontrolü). */
  rowHighlight?: (row: ApiRecord) => boolean;
  /** true ise rapor sayfası bir başlangıç/bitiş tarihi filtresi gösterir ve
   * bunları `start_date`/`end_date` query param'ı olarak endpoint'e ekler. */
  dateRange?: boolean;
}

function formatDate(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  const [year, month, day] = String(value).split('-');
  if (!year || !month || !day) return String(value);
  return `${day}.${month}.${year}`;
}

function formatDays(value: unknown): string {
  if (value === null || value === undefined) return '—';
  return `${String(value)} gün`;
}

function formatMonths(value: unknown): string {
  if (value === null || value === undefined) return '—';
  return `${String(value)} ay`;
}

function formatPercent(value: unknown): string {
  if (value === null || value === undefined) return '—';
  return `%${String(value)}`;
}

function formatPlain(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  return String(value);
}

function formatKg(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  return `${String(value)} kg`;
}

function formatDosage(value: unknown, row: ApiRecord): string {
  if (value === null || value === undefined || value === '') return '—';
  const unit = row.dosage_unit_name;
  return unit ? `${String(value)} ${String(unit)}` : String(value);
}

function formatKgPerDay(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  return `${String(value)} kg/gün`;
}

function formatCurrency(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  return `${String(value)} ₺`;
}

function formatUsd(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  return `$${String(value)}`;
}

export const reports: ReportConfig[] = [
  {
    slug: 'calving',
    title: 'Doğum/Buzağılama Raporu',
    description:
      'Belirtilen tarih aralığında doğan hayvanlar; cinsiyet, doğum tipi (tekiz/ikiz) ve doğum ağırlığı ile birlikte. Güç doğum (distoni) vakaları vurgulu.',
    endpoint: '/reports/calving',
    dateRange: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'mother_tag_number', label: 'Anne Küpe No', format: formatPlain },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate },
      { key: 'gender_name', label: 'Cinsiyet' },
      { key: 'birth_type_name', label: 'Doğum Şekli', format: formatPlain },
      { key: 'litter_type_name', label: 'Doğum Tipi', format: formatPlain },
      { key: 'birth_weight_kg', label: 'Doğum Ağırlığı', format: formatKg },
    ],
    rowHighlight: (row) => Boolean(row.is_difficult_birth),
  },
  {
    slug: 'breeding-performance',
    title: 'Tohumlama Performans Raporu',
    description:
      'Aralıktaki aşım kayıtları; doğal/suni tohumlama dağılımı, boğa veya sperma partisi bazında gebe kalma oranı.',
    endpoint: '/reports/breeding-performance',
    dateRange: true,
    columns: [
      { key: 'source_type', label: 'Yöntem' },
      { key: 'source_label', label: 'Boğa / Sperma Partisi' },
      { key: 'service_count', label: 'Tohumlama Sayısı' },
      { key: 'pregnant_count', label: 'Gebe Kalan' },
      { key: 'open_count', label: 'Boş Çıkan' },
      { key: 'suspicious_count', label: 'Şüpheli' },
      { key: 'pending_count', label: 'Kontrol Bekliyor' },
      { key: 'pregnancy_rate', label: 'Gebe Kalma Oranı', format: formatPercent },
    ],
    rowHighlight: (row) => typeof row.pregnancy_rate === 'number' && row.pregnancy_rate < 40,
  },
  {
    slug: 'pregnancy-check-results',
    title: 'Gebelik Kontrol Sonuçları Özeti',
    description: 'Aralıkta yapılan gebelik kontrolleri; hayvan, kontrol yöntemi ve sonuç bazında.',
    endpoint: '/reports/pregnancy-check-results',
    dateRange: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'service_date', label: 'Tohumlama Tarihi', format: formatDate },
      { key: 'check_date', label: 'Kontrol Tarihi', format: formatDate },
      { key: 'method_name', label: 'Kontrol Yöntemi' },
      { key: 'result_name', label: 'Sonuç' },
    ],
    rowHighlight: (row) => Boolean(row.is_suspicious),
  },
  {
    slug: 'health-events',
    title: 'Sağlık Olayları Raporu',
    description: 'Aralıktaki hastalık/tedavi kayıtları; hastalık dağılımı, ilaç kullanım sıklığı.',
    endpoint: '/reports/health-events',
    dateRange: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'event_date', label: 'Tarih', format: formatDate },
      { key: 'event_type_name', label: 'Olay Tipi' },
      { key: 'disease_name', label: 'Hastalık/Tanı', format: formatPlain },
      { key: 'medication_name', label: 'İlaç', format: formatPlain },
      { key: 'dosage_amount', label: 'Doz', format: formatDosage },
      { key: 'veterinarian_note', label: 'Veteriner Notu', format: formatPlain },
    ],
    rowHighlight: (row) => Boolean(row.is_illness),
  },
  {
    slug: 'weight-gains',
    title: 'Kilo Alım (ADG) Raporu',
    description:
      'Aralıkta en az iki tartısı olan hayvanlar için, ilk ve son tartı arasındaki günlük ortalama canlı ağırlık artışı (ADG).',
    endpoint: '/reports/weight-gains',
    dateRange: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'first_weigh_date', label: 'İlk Tartı', format: formatDate },
      { key: 'first_weight_kg', label: 'İlk Kilo', format: formatKg },
      { key: 'last_weigh_date', label: 'Son Tartı', format: formatDate },
      { key: 'last_weight_kg', label: 'Son Kilo', format: formatKg },
      { key: 'weight_gain_kg', label: 'Kilo Artışı', format: formatKg },
      { key: 'days_between', label: 'Gün Sayısı', format: formatDays },
      { key: 'average_daily_gain_kg', label: 'Günlük Ort. Artış (ADG)', format: formatKgPerDay },
    ],
    rowHighlight: (row) => typeof row.average_daily_gain_kg === 'number' && row.average_daily_gain_kg < 0,
  },
  {
    slug: 'sales',
    title: 'Satış Raporu',
    description: 'Aralıktaki satışlar; toplam gelir, ortalama satış ağırlığı/fiyatı, alıcı bazında kırılım.',
    endpoint: '/reports/sales',
    dateRange: true,
    columns: [
      { key: 'buyer_name', label: 'Alıcı' },
      { key: 'sale_count', label: 'Satış Sayısı' },
      { key: 'total_weight_kg', label: 'Toplam Ağırlık', format: formatKg },
      { key: 'total_revenue', label: 'Toplam Gelir', format: formatCurrency },
      { key: 'average_sale_amount', label: 'Ort. Satış Tutarı', format: formatCurrency },
      { key: 'average_price_per_kg', label: 'Ort. Kg Fiyatı', format: formatCurrency },
    ],
  },
  {
    slug: 'deaths',
    title: 'Ölüm/Kayıp Raporu',
    description: 'Aralıktaki ölümler; buzağı (0-7 ay) ve yetişkin kaybı ayrı ayrı, neden dağılımı ve kayıp oranı.',
    endpoint: '/reports/deaths',
    dateRange: true,
    columns: [
      { key: 'age_group', label: 'Yaş Grubu' },
      { key: 'death_count', label: 'Kayıp Sayısı' },
      { key: 'reason_breakdown', label: 'Neden Dağılımı', format: formatPlain },
      { key: 'current_active_count', label: 'Mevcut Aktif Sayı' },
      { key: 'loss_rate', label: 'Kayıp Oranı', format: formatPercent },
    ],
    rowHighlight: (row) => typeof row.loss_rate === 'number' && row.loss_rate >= 10,
  },
  {
    slug: 'herd-flow',
    title: 'Sürü Giriş-Çıkış Özeti',
    description: 'Aralıkta işletmeye giren (doğum/satın alma) ve çıkan (satış/ölüm) hayvan sayıları; net büyüme.',
    endpoint: '/reports/herd-flow',
    dateRange: true,
    columns: [
      { key: 'category', label: 'Hareket' },
      { key: 'count', label: 'Hayvan Sayısı' },
    ],
    rowHighlight: (row) => row.direction === 'Net',
  },
  {
    slug: 'feed-consumption',
    title: 'Yem Tüketim Raporu',
    description: 'Aralıkta dağıtılan yem miktarı, padok/yem tipi bazında.',
    endpoint: '/reports/feed-consumption',
    dateRange: true,
    columns: [
      { key: 'pen_code', label: 'Padok Kodu' },
      { key: 'pen_name', label: 'Padok Adı' },
      { key: 'feed_item_name', label: 'Yem Ürünü' },
      { key: 'feed_type_name', label: 'Yem Tipi' },
      { key: 'total_quantity_kg', label: 'Toplam Miktar', format: formatKg },
      { key: 'distribution_count', label: 'Dağıtım Sayısı' },
    ],
  },
  {
    slug: 'calving-intervals',
    title: 'Yavrulama Aralığı (Calving Interval) Raporu',
    description:
      'Her inek için son iki doğumu arasındaki gün farkı ve sürü ortalaması. Tarih aralığı gerektirmez. 400 günü aşanlar vurgulu.',
    endpoint: '/reports/calving-intervals',
    columns: [
      { key: 'tag_number', label: 'Hayvan' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'previous_calving_date', label: 'Önceki Doğum', format: formatDate },
      { key: 'last_calving_date', label: 'Son Doğum', format: formatDate },
      { key: 'interval_days', label: 'Yavrulama Aralığı', format: formatDays },
      { key: 'calving_count', label: 'Toplam Doğum Sayısı' },
    ],
    rowHighlight: (row) => Boolean(row.is_summary) || (typeof row.interval_days === 'number' && row.interval_days > 400),
  },
  {
    slug: 'breeding-candidates',
    title: 'Tohumlanacak Hayvanlar',
    description:
      '12 ay yaşına ulaşan düveler, doğum sonrası bekleme süresini (45 gün) tamamlamış inekler ve gebelik kontrolünde "Boş" çıkan hayvanlar.',
    endpoint: '/reports/breeding-candidates',
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'age_months', label: 'Yaş', format: formatMonths },
      { key: 'reason', label: 'Sebep' },
      { key: 'last_calving_date', label: 'Son Doğum Tarihi', format: formatDate },
      { key: 'last_service_date', label: 'Son Tohumlama Tarihi', format: formatDate },
    ],
    rowHighlight: (row) => row.reason === 'Tekrar Kızgınlık / Boş',
  },
  {
    slug: 'bred-animals',
    title: 'Tohumlu Hayvanlar',
    description: 'Tohumlaması yapılmış, aktif üreme döngüsündeki hayvanlar. Gebelik kontrolü gerekenler üstte listelenir.',
    endpoint: '/reports/bred-animals',
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'service_date', label: 'Tohumlama Tarihi', format: formatDate },
      { key: 'service_method_name', label: 'Yöntem' },
      { key: 'days_since_service', label: 'Geçen Süre', format: formatDays },
      { key: 'check_status', label: 'Durum' },
      { key: 'expected_calving_date', label: 'Beklenen Doğum', format: formatDate },
    ],
    rowHighlight: (row) => Boolean(row.pregnancy_check_due),
  },
  {
    slug: 'repeat-breeders',
    title: 'Tekrar Kızgınlık / Boş Çıkanlar',
    description: 'Gebelik kontrolünde "Boş" sonucu çıkmış, henüz yeniden tohumlanmamış hayvanlar.',
    endpoint: '/reports/repeat-breeders',
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'last_service_date', label: 'Son Tohumlama Tarihi', format: formatDate },
      { key: 'days_open', label: 'Açık Süre', format: formatDays },
      { key: 'service_method_name', label: 'Yöntem' },
    ],
    rowHighlight: () => true,
  },
  {
    slug: 'pregnant-animals',
    title: 'Gebe Hayvanlar',
    description: 'Gebeliği onaylanmış hayvanlar, beklenen doğum tarihine göre sıralı.',
    endpoint: '/reports/pregnant-animals',
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'service_date', label: 'Tohumlama Tarihi', format: formatDate },
      { key: 'expected_calving_date', label: 'Beklenen Doğum Tarihi', format: formatDate },
      { key: 'days_until_calving', label: 'Doğuma Kalan Süre', format: formatDays },
    ],
    rowHighlight: (row) => typeof row.days_until_calving === 'number' && row.days_until_calving <= 14,
  },
  {
    slug: 'active-animals',
    title: 'Aktif Hayvanlar',
    description: 'Tüm aktif hayvanlar, yaş (ay) dahil.',
    endpoint: '/reports/active-animals',
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'gender_name', label: 'Cinsiyet' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate },
      { key: 'age_months', label: 'Yaş', format: formatMonths },
      { key: 'mother_tag_number', label: 'Anne Küpe No', format: formatPlain },
    ],
  },
  {
    slug: 'calves',
    title: 'Buzağı Listesi (0-7 Ay)',
    description: '0-7 ay yaşındaki aktif hayvanlar.',
    endpoint: '/reports/calves',
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'gender_name', label: 'Cinsiyet' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate },
      { key: 'age_months', label: 'Yaş', format: formatMonths },
      { key: 'mother_tag_number', label: 'Anne Küpe No', format: formatPlain },
    ],
  },
  {
    slug: 'heifers-steers',
    title: 'Düve ve Dana Listesi (7-12 Ay)',
    description: '7-12 ay yaşındaki aktif hayvanlar (dişi: düve, erkek: dana).',
    endpoint: '/reports/heifers-steers',
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'gender_name', label: 'Cinsiyet' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate },
      { key: 'age_months', label: 'Yaş', format: formatMonths },
      { key: 'mother_tag_number', label: 'Anne Küpe No', format: formatPlain },
    ],
  },
  {
    slug: 'pen-occupancy',
    title: 'Padok Doluluk Durumu',
    description: 'Padokların kapasite ve güncel doluluk oranları.',
    endpoint: '/reports/pen-occupancy',
    columns: [
      { key: 'code', label: 'Kod' },
      { key: 'name', label: 'Ad' },
      { key: 'capacity', label: 'Kapasite', format: formatPlain },
      { key: 'current_count', label: 'Mevcut Sayı' },
      { key: 'occupancy_rate', label: 'Doluluk Oranı', format: formatPercent },
    ],
    rowHighlight: (row) => typeof row.occupancy_rate === 'number' && row.occupancy_rate >= 100,
  },
  {
    slug: 'pen-efficiency',
    title: 'Padok Maliyet-Verimlilik Raporu',
    description:
      'Aralıkta padoğa dağıtılan yem (miktar, TL ve TCMB kuruyla USD) ile o padoktaki hayvanların gerçek kilo artışı karşılaştırılır: yem dönüşüm oranı (FCR) ve kg canlı ağırlık başına maliyet.',
    endpoint: '/reports/pen-efficiency',
    dateRange: true,
    columns: [
      { key: 'code', label: 'Padok Kodu' },
      { key: 'name', label: 'Padok Adı' },
      { key: 'total_feed_quantity_kg', label: 'Toplam Yem', format: formatKg },
      { key: 'total_feed_cost_try', label: 'Yem Maliyeti (TL)', format: formatCurrency },
      { key: 'total_feed_cost_usd', label: 'Yem Maliyeti ($)', format: formatUsd },
      { key: 'total_weight_gain_kg', label: 'Toplam Kilo Artışı', format: formatKg },
      { key: 'feed_conversion_ratio', label: 'Yem Dönüşüm Oranı (FCR)', format: formatPlain },
      { key: 'cost_per_kg_gain_try', label: 'Kg Artış Başına Maliyet (TL)', format: formatCurrency },
      { key: 'cost_per_kg_gain_usd', label: 'Kg Artış Başına Maliyet ($)', format: formatUsd },
    ],
  },
  {
    slug: 'animal-profitability',
    title: 'Hayvan Kârlılık Raporu',
    description:
      'Aralıkta satılan veya ölen hayvanların yaşam boyu maliyeti (giriş değeri + sağlık + gün ağırlıklı yem payı) satış geliriyle karşılaştırılır. Giriş değeri, satın alınan hayvanlarda alım tutarı, işletmede doğanlarda ise doğumda biçilen tahmini değerdir - ölen bir hayvanın giriş değeri doğrudan zarar yazılır. TL tutarlar tarihsel/nominal, USD karşılığı işlem tarihindeki TCMB kuruyla hesaplanır. Zarar eden hayvanlar vurgulu.',
    endpoint: '/reports/animal-profitability',
    dateRange: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'outcome', label: 'Sonuç' },
      { key: 'outcome_date', label: 'Tarih', format: formatDate },
      { key: 'entry_value_try', label: 'Giriş Değeri (TL)', format: formatCurrency },
      { key: 'health_cost_try', label: 'Sağlık Maliyeti (TL)', format: formatCurrency },
      { key: 'feed_cost_try', label: 'Yem Payı (TL)', format: formatCurrency },
      { key: 'total_cost_try', label: 'Toplam Maliyet (TL)', format: formatCurrency },
      { key: 'total_cost_usd', label: 'Toplam Maliyet ($)', format: formatUsd },
      { key: 'revenue_try', label: 'Satış Geliri (TL)', format: formatCurrency },
      { key: 'revenue_usd', label: 'Satış Geliri ($)', format: formatUsd },
      { key: 'profit_try', label: 'Kâr/Zarar (TL)', format: formatCurrency },
      { key: 'profit_usd', label: 'Kâr/Zarar ($)', format: formatUsd },
    ],
    rowHighlight: (row) => typeof row.profit_try === 'number' && row.profit_try < 0,
  },
  {
    slug: 'herd-cost-summary',
    title: 'Sürü Genel Maliyet-Gelir Özeti',
    description:
      'Aralıkta gerçekleşen yem, sağlık ve alım maliyeti ile satış gelirinin TL ve USD (her kalemin kendi tarihindeki TCMB kuruyla) genel özeti - planlama için.',
    endpoint: '/reports/herd-cost-summary',
    dateRange: true,
    columns: [
      { key: 'category', label: 'Kalem' },
      { key: 'amount_try', label: 'Tutar (TL)', format: formatCurrency },
      { key: 'amount_usd', label: 'Tutar ($)', format: formatUsd },
    ],
    rowHighlight: (row) => row.category === 'Net (Gelir - Maliyet)',
  },
  {
    slug: 'herd-asset-value',
    title: 'Sürü Varlık Değeri Değişimi',
    description:
      'Bilanço yaklaşımıyla kârlılık: dönem başı ve dönem sonu itibarıyla yaşayan tüm hayvanların (demirbaş: inek/damızlık boğa amortismanlı, malzeme: buzağı/besi hayvanı birikmiş maliyetli) toplam defter değeri karşılaştırılır. Hayvan Kârlılık Raporu\'ndaki gerçekleşmiş (satış/ölüm) kâr/zararla birebir toplanmaz - farklı bir gösterge, sürünün toplam değer artışını/azalışını gösterir.',
    endpoint: '/reports/herd-asset-value',
    dateRange: true,
    columns: [
      { key: 'category', label: 'Kalem' },
      { key: 'amount_try', label: 'Tutar (TL)', format: formatCurrency },
      { key: 'amount_usd', label: 'Tutar ($)', format: formatUsd },
    ],
    rowHighlight: (row) => typeof row.category === 'string' && row.category.startsWith('Net Değişim'),
  },
];

export function getReport(slug: string): ReportConfig | undefined {
  return reports.find((r) => r.slug === slug);
}

/**
 * İki tarih arasında filtrelenebilecek, henüz yapım aşamasındaki genel
 * raporların planı (bkz. /reports hub sayfası). `slug` bir rapor
 * uygulandığında dolar; o zamana kadar hub sayfasında "Yakında" gösterilir.
 */
export interface GeneralReportPlan {
  title: string;
  description: string;
  slug: string | null;
}

export const generalReportPlans: GeneralReportPlan[] = [
  {
    title: 'Doğum/Buzağılama Raporu',
    description:
      'Belirtilen tarih aralığında doğum yapan hayvanlar; buzağı sayısı, cinsiyet dağılımı, tekiz/ikiz oranı ve güç doğum (distoni) vakaları vurgulu.',
    slug: 'calving',
  },
  {
    title: 'Tohumlama Performans Raporu',
    description: 'Aralıktaki aşım kayıtları; doğal/suni tohumlama dağılımı, boğa veya sperma partisi bazında gebe kalma oranı.',
    slug: 'breeding-performance',
  },
  {
    title: 'Gebelik Kontrol Sonuçları Özeti',
    description: 'Aralıkta yapılan gebelik kontrolleri; gebe/boş/şüpheli sonuç oranı.',
    slug: 'pregnancy-check-results',
  },
  {
    title: 'Sağlık Olayları Raporu',
    description: 'Aralıktaki hastalık/tedavi kayıtları; hastalık dağılımı, ilaç kullanım sıklığı.',
    slug: 'health-events',
  },
  {
    title: 'Kilo Alım (ADG) Raporu',
    description: 'Aralıktaki tartı kayıtlarından günlük ortalama kilo alımı, hayvan veya padok bazında.',
    slug: 'weight-gains',
  },
  {
    title: 'Satış Raporu',
    description: 'Aralıktaki satışlar; toplam gelir, ortalama satış ağırlığı/fiyatı, alıcı bazında kırılım.',
    slug: 'sales',
  },
  {
    title: 'Ölüm/Kayıp Raporu',
    description: 'Aralıktaki ölümler; buzağı (0-7 ay) ve yetişkin kaybı ayrı ayrı, neden dağılımı ve kayıp oranı.',
    slug: 'deaths',
  },
  {
    title: 'Sürü Giriş-Çıkış Özeti',
    description: 'Aralıkta işletmeye giren (doğum/satın alma) ve çıkan (satış/ölüm) hayvan sayıları; net büyüme.',
    slug: 'herd-flow',
  },
  {
    title: 'Yem Tüketim Raporu',
    description: 'Aralıkta dağıtılan yem miktarı, padok/yem tipi bazında.',
    slug: 'feed-consumption',
  },
  {
    title: 'Yavrulama Aralığı (Calving Interval) Raporu',
    description:
      'Her inek için son iki doğum arasındaki gün farkı ve sürü ortalaması. Tarih aralığı gerektirmez, hedefi (365/400 gün) aşanlar vurgulu - yavaş değişen ama verimliliği gösteren bir gösterge.',
    slug: 'calving-intervals',
  },
  {
    title: 'Padok Maliyet-Verimlilik Raporu',
    description:
      'Aralıkta padoğa dağıtılan yem (miktar, TL ve USD) ile o padoktaki hayvanların gerçek kilo artışı karşılaştırılır: yem dönüşüm oranı (FCR) ve kg canlı ağırlık başına maliyet.',
    slug: 'pen-efficiency',
  },
  {
    title: 'Hayvan Kârlılık Raporu',
    description:
      'Aralıkta satılan veya ölen hayvanların yaşam boyu maliyeti (giriş değeri + sağlık + yem payı) satış geliriyle karşılaştırılır. TL ve TCMB kuruyla USD.',
    slug: 'animal-profitability',
  },
  {
    title: 'Sürü Genel Maliyet-Gelir Özeti',
    description: 'Aralıkta gerçekleşen yem, sağlık ve giriş değeri maliyeti ile satış gelirinin TL/USD genel özeti - planlama için.',
    slug: 'herd-cost-summary',
  },
  {
    title: 'Sürü Varlık Değeri Değişimi',
    description:
      'Bilanço yaklaşımıyla kârlılık: yaşayan tüm hayvanların (demirbaş amortismanlı, malzeme birikmiş maliyetli) toplam defter değerindeki dönemsel artış/azalış.',
    slug: 'herd-asset-value',
  },
];
