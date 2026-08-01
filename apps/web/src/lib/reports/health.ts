import type { ReportConfig } from './types';
import { formatDate, formatDays, formatDosage, formatPlain } from './formatters';

/** Sağlık ve ilaç arınma süresi raporları. */
export const healthReports: ReportConfig[] = [
  {
    slug: 'health-events',
    title: 'Sağlık Olayları Raporu',
    description: 'Aralıktaki hastalık/tedavi kayıtları; hastalık dağılımı, ilaç kullanım sıklığı.',
    endpoint: '/reports/health-events',
    group: 'Sağlık',
    dateRange: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'event_date', label: 'Tarih', format: formatDate, width: 'narrow' },
      { key: 'event_type_name', label: 'Olay Tipi', width: 'narrow' },
      { key: 'disease_name', label: 'Hastalık/Tanı', format: formatPlain, width: 'narrow' },
      { key: 'medication_name', label: 'İlaç', format: formatPlain, width: 'narrow' },
      { key: 'dosage_amount', label: 'Doz', format: formatDosage, width: 'narrow' },
      { key: 'veterinarian_note', label: 'Veteriner Notu', format: formatPlain, width: 'wide' },
    ],
    rowHighlight: (row) => Boolean(row.is_illness),
  },
  {
    slug: 'withdrawal-periods',
    title: 'İlaç Arınma Süresi Devam Edenler',
    description:
      'Arınma süresi (ilacın vücuttan tamamen atıldığı, satışa/kesime uygun hale geldiği süre) henüz dolmamış aktif hayvanlar.',
    endpoint: '/reports/withdrawal-periods',
    group: 'Sağlık',
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'medication_name', label: 'İlaç', width: 'narrow' },
      { key: 'event_date', label: 'Uygulama Tarihi', format: formatDate, width: 'narrow' },
      { key: 'withdrawal_end_date', label: 'Arınma Bitiş Tarihi', format: formatDate, width: 'narrow' },
      { key: 'days_remaining', label: 'Kalan Gün', format: formatDays, width: 'narrow' },
    ],
  },
];
