import type { ApiRecord } from './api';
import { formatDateDMY as formatDate } from './format';

export interface ReportColumn {
  key: string;
  label: string;
  format?: (value: unknown, row: ApiRecord) => string;
  /** Sütun genişlik sınıfı - A4 baskıya uygun mizanpaj için:
   * 'narrow' = kısa değerler (tarih, yaş, sayı, kod) - başta/sonda 1
   *   karakterlik dolgu ile sıkışıklık hissi vermeden dar tutulur.
   * 'wide' = serbest metin (not, açıklama) - daha geniş ama TEK SATIR
   *   kalır, taşarsa "…" ile kesilir (üzerine gelince tam metin görünür).
   * Belirtilmezse normal (varsayılan) genişlik kullanılır. */
  width?: 'narrow' | 'wide';
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
  /** true ise rapor sayfası bir granülerlik (günlük/haftalık/aylık) seçici
   * gösterir ve bunu `granularity` query param'ı olarak endpoint'e ekler. */
  granularity?: boolean;
  /** true ise rapor sayfası tek bir "tarih itibariyle" filtresi gösterir
   * (aralık değil) ve bunu `as_of_date` query param'ı olarak endpoint'e ekler. */
  singleDate?: boolean;
  /** true ise rapor sayfası hayvan statüsü (Aktif/Satıldı/Öldü vb.) için
   * çoklu seçim checkbox filtresi gösterir; hiçbiri seçilmemiş ve form hiç
   * gönderilmemişse varsayılan olarak "Aktif" seçili gelir. Seçilenler
   * `status_ids` query param'ı olarak (tekrarlı) endpoint'e eklenir. */
  statusFilter?: boolean;
  /** true ise rapor sayfasının üstünde Büyüme Değerleme Çıpalarını
   * düzenleme sayfasına giden bir link gösterilir (bu rapor o verilere
   * dayandığı için). */
  usesGrowthCheckpoints?: boolean;
  /** Belirtilirse, rapor sayfasının üstünde açılabilir ("Bu rapor nasıl
   * çalışır?") bir açıklama metni gösterilir - raporun altındaki mantığı
   * (örn. doğum sonrası bekleme süresi gibi anlık görünmeyebilecek
   * kuralları) kullanıcıya açık şekilde anlatmak için. */
  helpNote?: string;
}

function formatDays(value: unknown): string {
  if (value === null || value === undefined) return '—';
  return `${String(value)} gün`;
}

export function formatMonths(value: unknown): string {
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

function formatReturnedFromPregnancy(value: unknown): string {
  return value === true ? '⚠ Önceden Gebeydi' : '—';
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

export function formatSourceCode(value: unknown): string {
  if (value === 'market_estimate') return 'Piyasa Tahmini';
  if (value === 'cost_basis') return 'Maliyet Bazlı';
  if (value === 'mixed') return 'Karışık';
  return '—';
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
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'mother_tag_number', label: 'Anne Küpe No', format: formatPlain, width: 'narrow' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate, width: 'narrow' },
      { key: 'gender_name', label: 'Cinsiyet', width: 'narrow' },
      { key: 'birth_type_name', label: 'Doğum Şekli', format: formatPlain },
      { key: 'litter_type_name', label: 'Doğum Tipi', format: formatPlain },
      { key: 'birth_weight_kg', label: 'Doğum Ağırlığı', format: formatKg, width: 'narrow' },
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
      { key: 'source_type', label: 'Yöntem', width: 'narrow' },
      { key: 'source_label', label: 'Boğa / Sperma Partisi', width: 'wide' },
      { key: 'service_count', label: 'Tohumlama Sayısı', width: 'narrow' },
      { key: 'pregnant_count', label: 'Gebe Kalan', width: 'narrow' },
      { key: 'open_count', label: 'Boş Çıkan', width: 'narrow' },
      { key: 'suspicious_count', label: 'Şüpheli', width: 'narrow' },
      { key: 'pending_count', label: 'Kontrol Bekliyor', width: 'narrow' },
      { key: 'pregnancy_rate', label: 'Gebe Kalma Oranı', format: formatPercent, width: 'narrow' },
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
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'service_date', label: 'Tohumlama Tarihi', format: formatDate, width: 'narrow' },
      { key: 'check_date', label: 'Kontrol Tarihi', format: formatDate, width: 'narrow' },
      { key: 'method_name', label: 'Kontrol Yöntemi' },
      { key: 'result_name', label: 'Sonuç', width: 'narrow' },
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
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'event_date', label: 'Tarih', format: formatDate, width: 'narrow' },
      { key: 'event_type_name', label: 'Olay Tipi' },
      { key: 'disease_name', label: 'Hastalık/Tanı', format: formatPlain },
      { key: 'medication_name', label: 'İlaç', format: formatPlain },
      { key: 'dosage_amount', label: 'Doz', format: formatDosage, width: 'narrow' },
      { key: 'veterinarian_note', label: 'Veteriner Notu', format: formatPlain, width: 'wide' },
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
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'first_weigh_date', label: 'İlk Tartı', format: formatDate, width: 'narrow' },
      { key: 'first_weight_kg', label: 'İlk Kilo', format: formatKg, width: 'narrow' },
      { key: 'last_weigh_date', label: 'Son Tartı', format: formatDate, width: 'narrow' },
      { key: 'last_weight_kg', label: 'Son Kilo', format: formatKg, width: 'narrow' },
      { key: 'weight_gain_kg', label: 'Kilo Artışı', format: formatKg, width: 'narrow' },
      { key: 'days_between', label: 'Gün Sayısı', format: formatDays, width: 'narrow' },
      { key: 'average_daily_gain_kg', label: 'Günlük Ort. Artış (ADG)', format: formatKgPerDay, width: 'narrow' },
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
      { key: 'sale_count', label: 'Satış Sayısı', width: 'narrow' },
      { key: 'total_weight_kg', label: 'Toplam Ağırlık', format: formatKg, width: 'narrow' },
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
      { key: 'age_group', label: 'Yaş Grubu', width: 'narrow' },
      { key: 'death_count', label: 'Kayıp Sayısı', width: 'narrow' },
      { key: 'reason_breakdown', label: 'Neden Dağılımı', format: formatPlain, width: 'wide' },
      { key: 'current_active_count', label: 'Mevcut Aktif Sayı', width: 'narrow' },
      { key: 'loss_rate', label: 'Kayıp Oranı', format: formatPercent, width: 'narrow' },
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
      { key: 'count', label: 'Hayvan Sayısı', width: 'narrow' },
    ],
    rowHighlight: (row) => row.direction_code === 'NET',
  },
  {
    slug: 'feed-consumption',
    title: 'Yem Tüketim Raporu',
    description: 'Aralıkta dağıtılan yem miktarı, padok/yem tipi bazında.',
    endpoint: '/reports/feed-consumption',
    dateRange: true,
    columns: [
      { key: 'pen_code', label: 'Padok Kodu', width: 'narrow' },
      { key: 'pen_name', label: 'Padok Adı' },
      { key: 'feed_item_name', label: 'Yem Ürünü' },
      { key: 'feed_type_name', label: 'Yem Tipi' },
      { key: 'total_quantity_kg', label: 'Toplam Miktar', format: formatKg, width: 'narrow' },
      { key: 'distribution_count', label: 'Dağıtım Sayısı', width: 'narrow' },
    ],
  },
  {
    slug: 'calving-intervals',
    title: 'Yavrulama Aralığı (Calving Interval) Raporu',
    description:
      'Her inek için son iki doğumu arasındaki gün farkı ve sürü ortalaması. Tarih aralığı gerektirmez. 400 günü aşanlar vurgulu.',
    endpoint: '/reports/calving-intervals',
    columns: [
      { key: 'tag_number', label: 'Hayvan', width: 'narrow' },
      { key: 'previous_calving_date', label: 'Önceki Doğum', format: formatDate, width: 'narrow' },
      { key: 'last_calving_date', label: 'Son Doğum', format: formatDate, width: 'narrow' },
      { key: 'interval_days', label: 'Yavrulama Aralığı', format: formatDays, width: 'narrow' },
      { key: 'calving_count', label: 'Toplam Doğum Sayısı', width: 'narrow' },
    ],
    rowHighlight: (row) => Boolean(row.is_summary) || (typeof row.interval_days === 'number' && row.interval_days > 400),
  },
  {
    slug: 'breeding-candidates',
    title: 'Tohumlanacak Hayvanlar',
    description:
      '12 ay yaşına ulaşan düveler, doğum yapmış inekler (doğum sonrası bekleme süresini tamamlayıp tamamlamadığına göre "Post Partum" veya "Tohumlanacak" olarak ayrılır) ve gebelik kontrolünde "Boş" çıkan (tekrar kızgınlık) hayvanlar - hepsi tek listede, Sebep sütunuyla ayırt edilir. "Boş" çıkanlar en uzun süredir açık olan üstte olacak şekilde sıralanır. Deneme Sayısı, son doğumundan bu yana kaç kez tohumlandığını gösterir - yüksek sayı fertilite sorununa işaret edebilir.',
    endpoint: '/reports/breeding-candidates',
    helpNote:
      'Bir hayvan doğurduğunda (buzağısı sisteme anne bilgisiyle kaydedildiğinde), o hayvan ANINDA "Gebe" statüsünden çıkar - bunun için ayrıca bir işlem yapmanıza gerek yoktur. Doğum yapan TÜM hayvanlar bu listede görünür, ama sebep sütunu ikiye ayrılır: doğumdan sonraki ilk 45 gün boyunca (toparlanma süresi) hayvan "Post Partum" olarak görünür - bu sadece bilgilendirme amaçlıdır, henüz bir aksiyon gerektirmez. 45 gün dolduğunda hayvan otomatik olarak "Tohumlanacak" sebebiyle listede görünmeye devam eder - artık tohumlanmaya hazır demektir. Dashboard\'daki "Tohumlanacak Hayvan" sayacı sadece gerçekten aksiyon gerektirenleri (Post Partum hariç) sayar.',
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'age_months', label: 'Yaş', format: formatMonths, width: 'narrow' },
      { key: 'reason', label: 'Sebep', width: 'wide' },
      { key: 'last_calving_date', label: 'Son Doğum Tarihi', format: formatDate, width: 'narrow' },
      { key: 'last_service_date', label: 'Son Tohumlama Tarihi', format: formatDate, width: 'narrow' },
      { key: 'days_open', label: 'Açık Süre', format: formatDays, width: 'narrow' },
      { key: 'service_method_name', label: 'Yöntem (Boş Çıkanlar)', format: formatPlain },
      { key: 'service_attempt_count', label: 'Deneme Sayısı', width: 'narrow' },
      { key: 'returned_from_pregnancy', label: 'Uyarı', format: formatReturnedFromPregnancy },
    ],
    rowHighlight: (row) => row.reason_code === 'open' || row.returned_from_pregnancy === true,
  },
  {
    slug: 'bred-animals',
    title: 'Tohumlu Hayvanlar',
    description:
      'Tohumlaması yapılmış, aktif üreme döngüsündeki hayvanlar. Gebelik kontrolü gerekenler üstte listelenir. Deneme Sayısı, son doğumundan bu yana (bu tohumlama dahil) kaçıncı deneme olduğunu gösterir. "⚠ Önceden Gebeydi" uyarısı, bu tohumlamadan önce aynı döngüde onaylı bir gebelik olduğunu ama artık geçerli olmadığını gösterir (sebebi - düşük mü, yanlış giriş mi - not alanına elle kaydedilmelidir).',
    endpoint: '/reports/bred-animals',
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'service_date', label: 'Tohumlama Tarihi', format: formatDate, width: 'narrow' },
      { key: 'service_method_name', label: 'Yöntem' },
      { key: 'days_since_service', label: 'Geçen Süre', format: formatDays, width: 'narrow' },
      { key: 'check_status', label: 'Durum', width: 'narrow' },
      { key: 'expected_calving_date', label: 'Beklenen Doğum', format: formatDate, width: 'narrow' },
      { key: 'service_attempt_count', label: 'Deneme Sayısı', width: 'narrow' },
      { key: 'returned_from_pregnancy', label: 'Uyarı', format: formatReturnedFromPregnancy },
    ],
    rowHighlight: (row) => Boolean(row.pregnancy_check_due) || row.returned_from_pregnancy === true,
  },
  {
    slug: 'pregnant-animals',
    title: 'Gebe Hayvanlar',
    description: 'Gebeliği onaylanmış hayvanlar, beklenen doğum tarihine göre sıralı.',
    endpoint: '/reports/pregnant-animals',
    helpNote:
      'Bir hayvan doğurduğunda (buzağısı sisteme anne bilgisiyle kaydedildiğinde) bu listeden ANINDA çıkar - ayrıca bir işlem yapmanıza gerek yoktur. Doğumdan sonra hayvan, Tohumlanacak Hayvanlar raporunda önce "Post Partum" (ilk 45 gün, toparlanma süresi) sonra "Tohumlanacak" (45 gün sonrası, tekrar tohumlamaya hazır) sebebiyle görünmeye devam eder.',
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'service_date', label: 'Tohumlama Tarihi', format: formatDate, width: 'narrow' },
      { key: 'expected_calving_date', label: 'Beklenen Doğum Tarihi', format: formatDate, width: 'narrow' },
      { key: 'days_until_calving', label: 'Doğuma Kalan Süre', format: formatDays, width: 'narrow' },
    ],
    rowHighlight: (row) => typeof row.days_until_calving === 'number' && row.days_until_calving <= 14,
  },
  {
    slug: 'active-animals',
    title: 'Hayvan Listesi (Durum Filtresi)',
    description:
      'Seçilen statülerdeki (varsayılan: Aktif) hayvanlar, yaş (ay) dahil. Satılan/ölen hayvanları da görmek için ilgili statüleri işaretleyin. CSV olarak indirilebilir.',
    endpoint: '/reports/active-animals',
    statusFilter: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'gender_name', label: 'Cinsiyet', width: 'narrow' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate, width: 'narrow' },
      { key: 'age_months', label: 'Yaş', format: formatMonths, width: 'narrow' },
      { key: 'mother_tag_number', label: 'Anne Küpe No', format: formatPlain, width: 'narrow' },
    ],
  },
  {
    slug: 'calves',
    title: 'Buzağı Listesi (0-7 Ay)',
    description: '0-7 ay yaşındaki aktif hayvanlar.',
    endpoint: '/reports/calves',
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'gender_name', label: 'Cinsiyet', width: 'narrow' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate, width: 'narrow' },
      { key: 'age_months', label: 'Yaş', format: formatMonths, width: 'narrow' },
      { key: 'mother_tag_number', label: 'Anne Küpe No', format: formatPlain, width: 'narrow' },
    ],
  },
  {
    slug: 'heifers-steers',
    title: 'Düve ve Dana Listesi (7-12 Ay)',
    description: '7-12 ay yaşındaki aktif hayvanlar (dişi: düve, erkek: dana).',
    endpoint: '/reports/heifers-steers',
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'gender_name', label: 'Cinsiyet', width: 'narrow' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate, width: 'narrow' },
      { key: 'age_months', label: 'Yaş', format: formatMonths, width: 'narrow' },
      { key: 'mother_tag_number', label: 'Anne Küpe No', format: formatPlain, width: 'narrow' },
    ],
  },
  {
    slug: 'pen-occupancy',
    title: 'Padok Doluluk Durumu',
    description: 'Padokların kapasite ve güncel doluluk oranları.',
    endpoint: '/reports/pen-occupancy',
    columns: [
      { key: 'code', label: 'Kod', width: 'narrow' },
      { key: 'name', label: 'Ad' },
      { key: 'capacity', label: 'Kapasite', format: formatPlain, width: 'narrow' },
      { key: 'current_count', label: 'Mevcut Sayı', width: 'narrow' },
      { key: 'occupancy_rate', label: 'Doluluk Oranı', format: formatPercent, width: 'narrow' },
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
      { key: 'code', label: 'Padok Kodu', width: 'narrow' },
      { key: 'name', label: 'Padok Adı' },
      { key: 'total_feed_quantity_kg', label: 'Toplam Yem', format: formatKg, width: 'narrow' },
      { key: 'total_feed_cost_try', label: 'Yem Maliyeti (TL)', format: formatCurrency },
      { key: 'total_feed_cost_usd', label: 'Yem Maliyeti ($)', format: formatUsd },
      { key: 'total_weight_gain_kg', label: 'Toplam Kilo Artışı', format: formatKg, width: 'narrow' },
      { key: 'feed_conversion_ratio', label: 'Yem Dönüşüm Oranı (FCR)', format: formatPlain, width: 'narrow' },
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
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'outcome', label: 'Sonuç', width: 'narrow' },
      { key: 'outcome_date', label: 'Tarih', format: formatDate, width: 'narrow' },
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
    rowHighlight: (row) => row.category_code === 'NET',
  },
  {
    slug: 'herd-market-value-series',
    title: 'Sürü Tahmini Piyasa Değeri',
    description:
      'Yaşayan tüm sürünün toplam tahmini piyasa değerinin zaman içindeki seyri - büyüme çıpası girilmiş genç hayvanlar için piyasa tahmini, diğerleri için maliyet-bazlı defter değeri toplanır (bkz. Sürü Hayvan Listesi).',
    endpoint: '/reports/herd-market-value-series',
    dateRange: true,
    granularity: true,
    usesGrowthCheckpoints: true,
    columns: [
      { key: 'date', label: 'Tarih', format: formatDate, width: 'narrow' },
      { key: 'amount_try', label: 'Tutar (TL)', format: formatCurrency },
      { key: 'amount_usd', label: 'Tutar ($)', format: formatUsd },
      { key: 'source_code', label: 'Kaynak', format: formatSourceCode },
    ],
  },
  {
    slug: 'herd-animal-market-values',
    title: 'Sürü Hayvan Listesi - Tahmini Piyasa Değeri',
    description:
      'Belirtilen tarih itibarıyla yaşayan TÜM hayvanların tahmini piyasa değeri tek tek listelenir (bkz. Sürü Tahmini Piyasa Değeri - o rapor toplamı, bu rapor dökümü verir). Alım/satım öncesi birden fazla hayvanı bir arada değerlendirmek için satırları işaretleyip seçilenlerin toplamını görebilirsiniz.',
    endpoint: '/reports/herd-animal-market-values',
    singleDate: true,
    usesGrowthCheckpoints: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'gender_name', label: 'Cinsiyet', width: 'narrow' },
      { key: 'age_months', label: 'Yaş', format: formatMonths, width: 'narrow' },
      { key: 'amount_try', label: 'Tutar (TL)', format: formatCurrency },
      { key: 'amount_usd', label: 'Tutar ($)', format: formatUsd },
      { key: 'source_code', label: 'Kaynak', format: formatSourceCode },
    ],
  },
];

export function getReport(slug: string): ReportConfig | undefined {
  return reports.find((r) => r.slug === slug);
}

/** /reports hub sayfasında listelenen (filtreli) raporlar - reports[]'ten türetilir. */
export function dateRangeReports(): ReportConfig[] {
  return reports.filter((r) => r.dateRange || r.singleDate || r.statusFilter);
}
