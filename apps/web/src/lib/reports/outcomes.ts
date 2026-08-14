import type { ReportConfig } from './types';
import { formatCurrency, formatDate, formatDays, formatExitAgeMixed, formatKg, formatPercent, formatPlain } from './formatters';

/** Sürüden çıkış raporları: satış, ölüm/kayıp, giriş-çıkış özeti. */
export const outcomeReports: ReportConfig[] = [
  {
    slug: 'sales',
    title: 'Satış Raporu',
    description:
      'Aralıktaki satışlar; alıcı VE satış tipi bazında kırılım (Canlı/Kesim/Damızlık farklı fiyatlama mantığına sahip olduğu için karıştırılmaz). Kg başına fiyat, sadece o ağırlığın girildiği satışların gelirinden hesaplanır. Randıman (karkas/canlı oranı), sadece her iki ağırlığın da girildiği kesim satışlarından ortalanır.',
    endpoint: '/reports/sales',
    group: 'Satış ve Kayıp',
    dateRange: true,
    columns: [
      { key: 'buyer_name', label: 'Alıcı', width: 'narrow' },
      { key: 'sale_type_name', label: 'Satış Tipi', width: 'narrow' },
      { key: 'sale_count', label: 'Satış Sayısı', width: 'narrow' },
      { key: 'total_live_weight_kg', label: 'Toplam Canlı Ağırlık', format: formatKg, width: 'narrow' },
      { key: 'average_price_per_live_kg', label: 'Ort. Canlı Kg Fiyatı', format: formatCurrency, width: 'narrow' },
      { key: 'total_carcass_weight_kg', label: 'Toplam Karkas Ağırlığı', format: formatKg, width: 'narrow' },
      {
        key: 'average_price_per_carcass_kg',
        label: 'Ort. Karkas Kg Fiyatı',
        format: formatCurrency,
        width: 'narrow',
      },
      { key: 'average_dressing_percentage', label: 'Ort. Randıman', format: formatPercent, width: 'narrow' },
      { key: 'total_revenue', label: 'Toplam Gelir', format: formatCurrency, width: 'narrow' },
      { key: 'average_sale_amount', label: 'Ort. Satış Tutarı', format: formatCurrency, width: 'narrow' },
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
  {
    slug: 'herd-exits',
    title: 'Sürüden Çıkış Raporu',
    description:
      'Aralıktaki satış ve ölüm çıkışlarını hayvan bazında birleştirir; sürüde kalma süresini ve varsa o hayvana ait geçmiş "Sürüden Çıkarma" yönlü değerlendirmeleri (tarih sırasıyla) gösterir - sübjektif değerlendirme notunu fiili çıkışla yan yana karşılaştırmak için.',
    endpoint: '/reports/herd-exits',
    group: 'Satış ve Kayıp',
    dateRange: true,
    defaultRangeDays: 365,
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'exit_type', label: 'Çıkış Tipi', width: 'narrow' },
      { key: 'exit_date', label: 'Çıkış Tarihi', format: formatDate, width: 'narrow' },
      { key: 'exit_age_months', label: 'Çıkış Yaşı', format: formatExitAgeMixed, width: 'narrow' },
      { key: 'herd_tenure_days', label: 'Sürüde Kalma Süresi', format: formatDays, width: 'narrow' },
      { key: 'culling_evaluation_reasons', label: 'Geçmiş Değerlendirme Nedenleri', format: formatPlain, width: 'wide' },
      { key: 'decision_to_exit_days', label: 'Son Değerlendirmeden Çıkışa Geçen Süre', format: formatDays, width: 'narrow' },
    ],
  },
];
