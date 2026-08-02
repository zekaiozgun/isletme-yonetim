import type { ReportConfig } from './types';
import { formatCurrency, formatKg, formatPercent, formatPlain } from './formatters';

/** Sürüden çıkış raporları: satış, ölüm/kayıp, giriş-çıkış özeti. */
export const outcomeReports: ReportConfig[] = [
  {
    slug: 'sales',
    title: 'Satış Raporu',
    description: 'Aralıktaki satışlar; toplam gelir, ortalama satış ağırlığı/fiyatı, alıcı bazında kırılım.',
    endpoint: '/reports/sales',
    group: 'Satış ve Kayıp',
    dateRange: true,
    columns: [
      { key: 'buyer_name', label: 'Alıcı', width: 'narrow' },
      { key: 'sale_count', label: 'Satış Sayısı', width: 'narrow' },
      { key: 'total_weight_kg', label: 'Toplam Ağırlık', format: formatKg, width: 'narrow' },
      { key: 'total_revenue', label: 'Toplam Gelir', format: formatCurrency, width: 'narrow' },
      { key: 'average_sale_amount', label: 'Ort. Satış Tutarı', format: formatCurrency, width: 'narrow' },
      { key: 'average_price_per_kg', label: 'Ort. Kg Fiyatı', format: formatCurrency, width: 'narrow' },
    ],
  },
  {
    slug: 'deaths',
    title: 'Ölüm/Kayıp Raporu',
    description:
      'Aralıktaki ölümler; buzağı (0-7 ay) ve yetişkin kaybı ayrı ayrı, neden dağılımı ve kayıp oranı. "Toplam" satırı ikisinin birleşik oranını gösterir - Dashboard\'daki "Yıllık Kayıp Oranı" ile karşılaştırmak için (o tek bir sürü-geneli oran verir, buradaki iki ayrı satır ağırlıklı ortalaması alınınca ona eşit olur).',
    endpoint: '/reports/deaths',
    group: 'Satış ve Kayıp',
    dateRange: true,
    defaultRangeDays: 365,
    columns: [
      { key: 'age_group', label: 'Yaş Grubu', width: 'narrow' },
      { key: 'death_count', label: 'Kayıp Sayısı', width: 'narrow' },
      { key: 'reason_breakdown', label: 'Neden Dağılımı', format: formatPlain, width: 'wide' },
      { key: 'current_active_count', label: 'Mevcut Aktif Sayı', width: 'narrow' },
      { key: 'loss_rate', label: 'Kayıp Oranı', format: formatPercent, width: 'narrow' },
    ],
    rowHighlight: (row) => Boolean(row.is_summary) || (typeof row.loss_rate === 'number' && row.loss_rate >= 10),
  },
  {
    slug: 'herd-flow',
    title: 'Sürü Giriş-Çıkış Özeti',
    description: 'Aralıkta işletmeye giren (doğum/satın alma) ve çıkan (satış/ölüm) hayvan sayıları; net büyüme.',
    endpoint: '/reports/herd-flow',
    group: 'Satış ve Kayıp',
    dateRange: true,
    defaultRangeDays: 365,
    columns: [
      { key: 'category', label: 'Hareket', width: 'narrow' },
      { key: 'count', label: 'Hayvan Sayısı', width: 'narrow' },
    ],
    rowHighlight: (row) => row.direction_code === 'NET',
  },
];
