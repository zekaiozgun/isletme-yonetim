import type { ApiRecord } from '@/lib/api';
import type { ReportConfig } from '@/lib/reports';
import { formatDate, formatDays, formatKg } from '@/lib/reports/formatters';
import { ReportTable } from '@/components/ReportTable';

const runwayReport: ReportConfig = {
  slug: 'feed-stock-runway',
  title: 'Yem Stok Tükenme Tahmini',
  description: '',
  group: 'Padok ve Yem',
  endpoint: '/reports/feed-stock-runway',
  columns: [
    { key: 'feed_item_name', label: 'Yem Ürünü', width: 'narrow' },
    { key: 'feed_type_name', label: 'Yem Tipi', width: 'narrow' },
    { key: 'stock_kg', label: 'Mevcut Stok', format: formatKg, width: 'narrow' },
    { key: 'daily_consumption_kg', label: 'Güncel Günlük Tüketim', format: formatKg, width: 'narrow' },
    { key: 'days_remaining', label: 'Kaç Gün Yeter', format: formatDays, width: 'narrow' },
    { key: 'estimated_depletion_date', label: 'Tahmini Tükenme Tarihi', format: formatDate, width: 'narrow' },
  ],
  rowHighlight: (row) => typeof row.days_remaining === 'number' && row.days_remaining < 7,
};

/** Günlük Rasyon Maliyeti ve Stok Tükenme Tahmini - tek rapor girişinden,
 * iki ayrı tabloya (bölüme) ayrılır: padok bazında günlük maliyet ve yem
 * kalemi bazında stok tükenme tahmini. İkisi de AYNI "an itibarıyla" (tek
 * tarih) anlayışını paylaşır - bkz. lib/reports/pens-feed.ts. */
export function DailyFeedCostSection({
  costReport,
  costRows,
  runwayRows,
}: {
  costReport: ReportConfig;
  costRows: ApiRecord[];
  runwayRows: ApiRecord[];
}) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Padok Bazında Günlük Maliyet
        </h2>
        <ReportTable report={costReport} rows={costRows} />
      </div>
      <div>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Yem Kalemi Bazında Stok Tükenme Tahmini
        </h2>
        <ReportTable report={runwayReport} rows={runwayRows} />
      </div>
    </div>
  );
}
