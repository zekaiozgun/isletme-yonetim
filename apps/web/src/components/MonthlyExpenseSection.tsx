import type { ApiRecord } from '@/lib/api';
import type { ReportConfig } from '@/lib/reports';
import { formatCurrency, formatDate, formatPlain } from '@/lib/reports/formatters';
import { ReportTable } from '@/components/ReportTable';

const detailReport: ReportConfig = {
  slug: 'monthly-expense-detail',
  title: 'Genel Gider Kayıtları',
  description: '',
  group: 'Mali',
  endpoint: '/reports/monthly-expense-detail',
  columns: [
    { key: 'expense_date', label: 'Tarih', format: formatDate, width: 'narrow' },
    { key: 'category_name', label: 'Kategori', width: 'narrow' },
    { key: 'amount', label: 'Tutar (TL)', format: formatCurrency, width: 'narrow' },
    { key: 'note', label: 'Açıklama', format: formatPlain, width: 'wide' },
  ],
};

/** Aylık Harcama Raporu - tek rapor girişinden iki bölüme ayrılır: Yem +
 * Sağlık/İlaç + kategori bazında Genel Giderler'in TL/USD özeti (üstte,
 * kayıtlı raporun kendi sütunlarıyla) ve altında o dönemdeki Genel Gider
 * kayıtlarının ham listesi (DailyFeedCostSection ile aynı iki-bölümlü
 * kompozisyon deseni). */
export function MonthlyExpenseSection({
  summaryReport,
  summaryRows,
  detailRows,
}: {
  summaryReport: ReportConfig;
  summaryRows: ApiRecord[];
  detailRows: ApiRecord[];
}) {
  return (
    <div className="space-y-8">
      <ReportTable report={summaryReport} rows={summaryRows} />
      <div>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Genel Gider Kayıtları</h2>
        <ReportTable report={detailReport} rows={detailRows} />
      </div>
    </div>
  );
}
