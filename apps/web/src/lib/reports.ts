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

export const reports: ReportConfig[] = [
  {
    slug: 'breeding-candidates',
    title: 'Tohumlanacak Hayvanlar',
    description: '12 ay yaşına ulaşan düveler ve doğum sonrası bekleme süresini (45 gün) tamamlamış inekler.',
    endpoint: '/reports/breeding-candidates',
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim', format: formatPlain },
      { key: 'age_months', label: 'Yaş', format: formatMonths },
      { key: 'reason', label: 'Sebep' },
      { key: 'last_calving_date', label: 'Son Doğum Tarihi', format: formatDate },
    ],
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
];

export function getReport(slug: string): ReportConfig | undefined {
  return reports.find((r) => r.slug === slug);
}
