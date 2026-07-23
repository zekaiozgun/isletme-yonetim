import { notFound } from 'next/navigation';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { getReport } from '@/lib/reports';
import { ReportTable } from '@/components/ReportTable';
import { DateRangeFilter } from '@/components/DateRangeFilter';

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
  searchParams: Promise<{ start?: string; end?: string }>;
}) {
  const { report: slug } = await params;
  const report = getReport(slug);
  if (!report) notFound();

  let rows: ApiRecord[] = [];
  let rangeStart: string | undefined;
  let rangeEnd: string | undefined;

  if (report.dateRange) {
    const sp = await searchParams;
    rangeStart = sp.start || firstDayOfMonthIso();
    rangeEnd = sp.end || todayIso();
    const separator = report.endpoint.includes('?') ? '&' : '?';
    rows = await apiGetSafe<ApiRecord[]>(
      `${report.endpoint}${separator}start_date=${rangeStart}&end_date=${rangeEnd}`,
      []
    );
  } else {
    rows = await apiGetSafe<ApiRecord[]>(report.endpoint, []);
  }

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">{report.title}</h1>
      <p className="mb-4 text-sm text-slate-500">{report.description}</p>
      {report.dateRange && rangeStart && rangeEnd && <DateRangeFilter start={rangeStart} end={rangeEnd} />}
      <ReportTable report={report} rows={rows} />
    </div>
  );
}
