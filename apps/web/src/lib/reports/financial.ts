import type { ReportConfig } from './types';
import { formatAgeMixed, formatCurrency, formatDate, formatGenderShort, formatPlain, formatSourceCode, formatUsd } from './formatters';

/** Mali/kârlılık raporları: hayvan bazlı kâr-zarar, sürü geneli maliyet-gelir özeti, tahmini piyasa değeri. */
export const financialReports: ReportConfig[] = [
  {
    slug: 'animal-profitability',
    title: 'Hayvan Kârlılık Raporu',
    description:
      'Aralıkta satılan veya ölen hayvanların yaşam boyu maliyeti (giriş değeri + sağlık + gün ağırlıklı yem payı) satış geliriyle karşılaştırılır. Giriş değeri, satın alınan hayvanlarda alım tutarı, işletmede doğanlarda ise doğumda biçilen tahmini değerdir - ölen bir hayvanın giriş değeri doğrudan zarar yazılır. TL tutarlar tarihsel/nominal, USD karşılığı işlem tarihindeki TCMB kuruyla hesaplanır. Zarar eden hayvanlar vurgulu.',
    endpoint: '/reports/animal-profitability',
    group: 'Mali',
    dateRange: true,
    defaultRangeDays: 365,
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'outcome', label: 'Sonuç', width: 'narrow' },
      { key: 'outcome_date', label: 'Tarih', format: formatDate, width: 'narrow' },
      { key: 'entry_value_try', label: 'Giriş Değeri (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'health_cost_try', label: 'Sağlık Maliyeti (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'feed_cost_try', label: 'Yem Payı (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'total_cost_try', label: 'Toplam Maliyet (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'total_cost_usd', label: 'Toplam Maliyet ($)', format: formatUsd, width: 'narrow' },
      { key: 'revenue_try', label: 'Satış Geliri (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'revenue_usd', label: 'Satış Geliri ($)', format: formatUsd, width: 'narrow' },
      { key: 'profit_try', label: 'Kâr/Zarar (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'profit_usd', label: 'Kâr/Zarar ($)', format: formatUsd, width: 'narrow' },
      { key: 'note', label: 'Not', format: formatPlain, width: 'wide' },
    ],
    rowHighlight: (row) => typeof row.profit_try === 'number' && row.profit_try < 0,
  },
  {
    slug: 'herd-profit-loss',
    title: 'Sürü Kâr/Zarar Raporu',
    description:
      'Seçilen dönemde sürünün özkaynak değişimini iki katmanda özetler: Ekonomik Sonuç (satış geliri, satın alma bedeli, yem/sağlık maliyeti ve piyasa değeri hareketinin birleşimi - tek bir "sermaye büyüdü mü küçüldü mü" cevabı) ve altında açılan Piyasa Değer Köprüsü (doğum, satın alma, ölüm, satış ve mevcut sürünün değer değişimiyle dönem başından sonuna kalem kalem geçiş). Doğumla giren değerin ne kadarının annenin gebelik dönemi yem maliyeti, ne kadarının gerçek doğum kârı olduğu ayrıca gösterilir. Varsayılan aralık 1 yıl - daha kısa geriye veri yoksa mevcut veriyle sınırlı kalır.',
    endpoint: '/reports/herd-profit-loss',
    group: 'Mali',
    dateRange: true,
    defaultRangeDays: 365,
    columns: [
      { key: 'start_date', label: 'Başlangıç', format: formatDate, width: 'narrow' },
      { key: 'end_date', label: 'Bitiş', format: formatDate, width: 'narrow' },
      { key: 'net_result_try', label: 'Net Kâr/Zarar (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'net_result_usd', label: 'Net Kâr/Zarar ($)', format: formatUsd, width: 'narrow' },
    ],
  },
  {
    slug: 'herd-cost-summary',
    title: 'Sürü Genel Maliyet-Gelir Özeti',
    description:
      'Aralıkta gerçekleşen yem, sağlık ve alım maliyeti ile satış gelirinin TL ve USD (her kalemin kendi tarihindeki TCMB kuruyla) genel özeti - planlama için.',
    endpoint: '/reports/herd-cost-summary',
    group: 'Mali',
    dateRange: true,
    columns: [
      { key: 'category', label: 'Kalem', width: 'narrow' },
      { key: 'amount_try', label: 'Tutar (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'amount_usd', label: 'Tutar ($)', format: formatUsd, width: 'narrow' },
    ],
    rowHighlight: (row) => row.category_code === 'NET',
  },
  {
    slug: 'herd-animal-market-values',
    title: 'Sürü Hayvan Listesi - Tahmini Piyasa Değeri',
    description:
      'Belirtilen tarih itibarıyla yaşayan TÜM hayvanların tahmini piyasa değeri tek tek listelenir - büyüme çıpası girilmiş genç hayvanlar için piyasa tahmini, diğerleri için maliyet-bazlı defter değeri kullanılır. Alım/satım öncesi birden fazla hayvanı bir arada değerlendirmek için satırları işaretleyip seçilenlerin toplamını görebilirsiniz.',
    endpoint: '/reports/herd-animal-market-values',
    group: 'Mali',
    singleDate: true,
    usesGrowthCheckpoints: true,
    columns: [
      { key: 'tag_number', label: 'Küpe No', width: 'narrow' },
      { key: 'gender_name', label: 'D/E', format: formatGenderShort, width: 'narrow' },
      { key: 'age_months', label: 'Yaş', format: formatAgeMixed, width: 'narrow' },
      { key: 'amount_try', label: 'Tutar (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'amount_usd', label: 'Tutar ($)', format: formatUsd, width: 'narrow' },
      { key: 'source_code', label: 'Kaynak', format: formatSourceCode, width: 'narrow' },
    ],
  },
];
