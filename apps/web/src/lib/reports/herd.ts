import type { ReportConfig } from './types';
import { formatDate, formatHerdStatusCategory, formatMonths, formatParentage, formatPlain, herdStatusRowClass } from './formatters';

/** Sürü kompozisyonu ve listeleme raporları: statü/yaş bazlı hayvan listeleri, sürü durum özeti. */
export const herdReports: ReportConfig[] = [
  {
    slug: 'active-animals',
    title: 'Hayvan Listesi (Durum Filtresi)',
    description:
      'Seçilen statülerdeki (varsayılan: Aktif) hayvanlar, yaş (ay) dahil. Satılan/ölen hayvanları da görmek için ilgili statüleri işaretleyin. CSV olarak indirilebilir.',
    endpoint: '/reports/active-animals',
    group: 'Sürü Listeleri',
    statusFilter: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'gender_name', label: 'Cinsiyet', width: 'narrow' },
      { key: 'breed_name', label: 'Irk', format: formatPlain, width: 'narrow' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate, width: 'narrow' },
      { key: 'age_months', label: 'Yaş', format: formatMonths, width: 'narrow' },
      { key: 'mother_tag_number', label: 'Anne/Baba', format: formatParentage, width: 'narrow' },
      { key: 'note', label: 'Not', format: formatPlain, width: 'wide' },
    ],
  },
  {
    slug: 'calves',
    title: 'Buzağı Listesi (0-7 Ay)',
    description: '0-7 ay yaşındaki aktif hayvanlar.',
    endpoint: '/reports/calves',
    group: 'Sürü Listeleri',
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'gender_name', label: 'Cinsiyet', width: 'narrow' },
      { key: 'breed_name', label: 'Irk', format: formatPlain, width: 'narrow' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate, width: 'narrow' },
      { key: 'age_months', label: 'Yaş', format: formatMonths, width: 'narrow' },
      { key: 'mother_tag_number', label: 'Anne/Baba', format: formatParentage, width: 'narrow' },
      { key: 'note', label: 'Not', format: formatPlain, width: 'wide' },
    ],
  },
  {
    slug: 'heifers-steers',
    title: 'Düve ve Dana Listesi (7-12 Ay)',
    description: '7-12 ay yaşındaki aktif hayvanlar (dişi: düve, erkek: dana).',
    endpoint: '/reports/heifers-steers',
    group: 'Sürü Listeleri',
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'gender_name', label: 'Cinsiyet', width: 'narrow' },
      { key: 'breed_name', label: 'Irk', format: formatPlain, width: 'narrow' },
      { key: 'birth_date', label: 'Doğum Tarihi', format: formatDate, width: 'narrow' },
      { key: 'age_months', label: 'Yaş', format: formatMonths, width: 'narrow' },
      { key: 'mother_tag_number', label: 'Anne/Baba', format: formatParentage, width: 'narrow' },
      { key: 'note', label: 'Not', format: formatPlain, width: 'wide' },
    ],
  },
  {
    slug: 'herd-status-summary',
    title: 'Sürü Durum Özeti',
    description:
      'Aktif sürünün tek tabloda özeti: yaş kovaları (Buzağı/Düve-Tosun/Yetişkin Erkek) ile doğurgan yaştaki dişilerin üreme alt-durumları (Tohumlanacak/Tohumlu/Şüpheli/Gebe) bir arada. "Doğurgan Yaştaki Dişi" satırı, altındaki 7 alt-durumun toplamına tam olarak eşittir.',
    endpoint: '/reports/herd-status-summary',
    group: 'Sürü Listeleri',
    columns: [
      { key: 'category', label: 'Kategori', format: formatHerdStatusCategory, width: 'wide', cellClassName: herdStatusRowClass },
      { key: 'count', label: 'Sayı', width: 'narrow', cellClassName: herdStatusRowClass },
    ],
  },
];
