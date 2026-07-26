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
  searchParams: Promise<{ start?: string; end?: string; as_of_date?: string; granularity?: string }>;
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

  const query = new URLSearchParams();
  if (rangeStart) query.set('start_date', rangeStart);
  if (rangeEnd) query.set('end_date', rangeEnd);
  if (asOfDate) query.set('as_of_date', asOfDate);
  if (granularity) query.set('granularity', granularity);
  const separator = report.endpoint.includes('?') ? '&' : '?';
  const rows = await apiGetSafe<ApiRecord[]>(`${report.endpoint}${separator}${query.toString()}`, []);

  const showCustomFilter = report.granularity || report.singleDate;

  return (
    <div>
      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-semibold text-slate-900">{report.title}</h1>
        {report.usesGrowthCheckpoints && (
          <Link
            href="/growth-valuation-checkpoints"
            className="text-sm font-medium text-slate-500 hover:text-slate-800 hover:underline"
          >
            Büyüme Değerleme Çıpalarını Düzenle →
          </Link>
        )}
      </div>
      <p className="mb-4 text-sm text-slate-500">{report.description}</p>
      {showCustomFilter ? (
        <MarketValueSeriesFilter
          start={rangeStart}
          end={rangeEnd}
          asOfDate={asOfDate}
          granularity={granularity}
          showDateRange={Boolean(report.dateRange)}
          showSingleDate={Boolean(report.singleDate)}
          showGranularity={Boolean(report.granularity)}
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
