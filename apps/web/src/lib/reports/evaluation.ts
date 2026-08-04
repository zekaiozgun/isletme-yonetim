import type { ReportConfig } from './types';
import { formatDate, formatPlain } from './formatters';

/** Sürü değerlendirme raporları: hem sürüden çıkarma hem damızlık önerisi
 * yönündeki değerlendirmeleri kapsar - tek bir sürü değerlendirmesi
 * felsefesinin iki kutbu (bkz. apps/api evaluation modülü). */
export const evaluationReports: ReportConfig[] = [
  {
    slug: 'animal-evaluations',
    title: 'Hayvan Değerlendirmeleri Raporu',
    description:
      'Aralıkta girilmiş tüm hayvan değerlendirmeleri (Sürüden Çıkarma + Damızlık Önerisi, tek listede). Değerlendirme statüsü/kapatması yoktur - her kayıt append-only bir gözlemdir, kullanıcı geçmişi yorumlar.',
    endpoint: '/reports/animal-evaluations',
    group: 'Değerlendirme',
    dateRange: true,
    defaultRangeDays: 365,
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'evaluation_date', label: 'Tarih', format: formatDate, width: 'narrow' },
      { key: 'direction_name', label: 'Yön', width: 'narrow' },
      { key: 'reason_name', label: 'Neden', width: 'narrow' },
      { key: 'priority_name', label: 'Öncelik', format: formatPlain, width: 'narrow' },
      { key: 'note', label: 'Not', format: formatPlain, width: 'wide' },
    ],
  },
  {
    slug: 'breeding-recommendations',
    title: 'Damızlık Önerileri',
    description:
      'Hâlâ aktif olan hayvanlardan "Damızlık Önerisi" yönünde işaretlenmiş değerlendirmeler - Tohumlama Adayları raporunun aksine otomatik/kural bazlı değil, insan değerlendirmesine dayalı bir izleme listesidir.',
    endpoint: '/reports/breeding-recommendations',
    group: 'Değerlendirme',
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'evaluation_date', label: 'Tarih', format: formatDate, width: 'narrow' },
      { key: 'reason_name', label: 'Neden', width: 'narrow' },
      { key: 'note', label: 'Not', format: formatPlain, width: 'wide' },
    ],
  },
];
