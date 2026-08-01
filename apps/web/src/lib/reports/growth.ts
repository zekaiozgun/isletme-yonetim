import type { ReportConfig } from './types';
import { formatDate, formatDays, formatKg, formatKgPerDay, formatPlain } from './formatters';

/** Kilo alımı / büyüme raporları. */
export const growthReports: ReportConfig[] = [
  {
    slug: 'weight-gains',
    title: 'Kilo Alım (ADG) Raporu',
    description:
      'Aralıkta en az iki tartısı olan hayvanlar için, ilk ve son tartı arasındaki günlük ortalama canlı ağırlık artışı (ADG).',
    endpoint: '/reports/weight-gains',
    dateRange: true,
    defaultRangeDays: 180,
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'first_weigh_date', label: 'İlk Tartı', format: formatDate, width: 'narrow' },
      { key: 'first_weight_kg', label: 'İlk Kilo', format: formatKg, width: 'narrow' },
      { key: 'last_weigh_date', label: 'Son Tartı', format: formatDate, width: 'narrow' },
      { key: 'last_weight_kg', label: 'Son Kilo', format: formatKg, width: 'narrow' },
      { key: 'weight_gain_kg', label: 'Kilo Artışı', format: formatKg, width: 'narrow' },
      { key: 'days_between', label: 'Gün Sayısı', format: formatDays, width: 'narrow' },
      { key: 'average_daily_gain_kg', label: 'Günlük Ort. Artış (ADG)', format: formatKgPerDay, width: 'narrow' },
      { key: 'note', label: 'Not', format: formatPlain, width: 'wide' },
    ],
    rowHighlight: (row) => typeof row.average_daily_gain_kg === 'number' && row.average_daily_gain_kg < 0,
  },
];
