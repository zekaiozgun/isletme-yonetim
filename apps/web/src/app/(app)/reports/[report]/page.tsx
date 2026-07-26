import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { getReport } from '@/lib/reports';
import { ReportTable } from '@/components/ReportTable';
import { HerdAnimalValueTable } from '@/components/HerdAnimalValueTable';
import { DateRangeFilter } from '@/components/DateRangeFilter';
import { MarketValueSeriesFilter } from '@/components/MarketValueSeriesFilter';

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function firstDayOfMonthIso(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
}

export default async function ReportPage({
  params,
  searchParams,
}: {
  params: Promise<{ report: string }>;
  searchParams: Promise<{
    start?: string;
    end?: string;
    as_of_date?: string;
    granularity?: string;
    filtered?: string;
    status_ids?: string | string[];
  }>;
}) {
  const { report: slug } = await params;
  const report = getReport(slug);
  if (!report) notFound();

  const sp = await searchParams;

  let rangeStart: string | undefined;
  let rangeEnd: string | undefined;
  if (report.dateRange) {
    rangeStart = sp.start || firstDayOfMonthIso();
    rangeEnd = sp.end || todayIso();
  }

  const asOfDate = report.singleDate ? sp.as_of_date || todayIso() : undefined;
  const granularity = report.granularity ? sp.granularity || 'monthly' : undefined;

  let statusOptions: { id: number; name: string }[] = [];
  let selectedStatusIds: number[] = [];
  if (report.statusFilter) {
    const statuses = await apiGetSafe<ApiRecord[]>('/animals/statuses', []);
    statusOptions = statuses.map((s) => ({ id: Number(s.id), name: String(s.name) }));
    if (sp.filtered === '1') {
      const raw = sp.status_ids;
      selectedStatusIds = raw ? (Array.isArray(raw) ? raw : [raw]).map(Number) : [];
    } else {
      const active = statuses.find((s) => s.code === 'AKTIF');
      selectedStatusIds = active ? [Number(active.id)] : [];
    }
  }

  const query = new URLSearchParams();
  if (rangeStart) query.set('start_date', rangeStart);
  if (rangeEnd) query.set('end_date', rangeEnd);
  if (asOfDate) query.set('as_of_date', asOfDate);
  if (granularity) query.set('granularity', granularity);
  for (const id of selectedStatusIds) query.append('status_ids', String(id));
  const separator = report.endpoint.includes('?') ? '&' : '?';
  const rows = await apiGetSafe<ApiRecord[]>(`${report.endpoint}${separator}${query.toString()}`, []);

  const showCustomFilter = report.granularity || report.singleDate || report.statusFilter;

  return (
    <div>
      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-semibold text-slate-900">{report.title}</h1>
        {report.usesGrowthCheckpoints && (
          <Link
            href="/growth-valuation-checkpoints"
            className="text-sm font-medium text-slate-500 hover:text-slate-800 hover:underline print:hidden"
          >
            Büyüme Değerleme Çıpalarını Düzenle →
          </Link>
        )}
      </div>
      <p className="mb-4 text-sm text-slate-500">{report.description}</p>
      {report.helpNote && (
        <details className="mb-4 rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600 print:hidden">
          <summary className="cursor-pointer font-medium text-slate-700">Bu rapor nasıl çalışır?</summary>
          <p className="mt-2">{report.helpNote}</p>
        </details>
      )}
      {showCustomFilter ? (
        <MarketValueSeriesFilter
          start={rangeStart}
          end={rangeEnd}
          asOfDate={asOfDate}
          granularity={granularity}
          statuses={report.statusFilter ? statusOptions : undefined}
          selectedStatusIds={report.statusFilter ? selectedStatusIds : undefined}
          showDateRange={Boolean(report.dateRange)}
          showSingleDate={Boolean(report.singleDate)}
          showGranularity={Boolean(report.granularity)}
          showStatusFilter={Boolean(report.statusFilter)}
        />
      ) : (
        report.dateRange && rangeStart && rangeEnd && <DateRangeFilter start={rangeStart} end={rangeEnd} />
      )}
      {report.slug === 'herd-animal-market-values' ? (
        <HerdAnimalValueTable rows={rows} />
      ) : (
        <ReportTable report={report} rows={rows} />
      )}
    </div>
  );
}
