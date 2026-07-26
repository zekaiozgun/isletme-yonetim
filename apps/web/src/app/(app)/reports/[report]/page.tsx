import { notFound } from 'next/navigation';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { getReport } from '@/lib/reports';
import { ReportTable } from '@/components/ReportTable';
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
  searchParams: Promise<{ start?: string; end?: string; granularity?: string; animal_id?: string }>;
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

  const granularity = report.granularity ? sp.granularity || 'monthly' : undefined;

  let animalId: string | undefined;
  let animalOptions: { id: string; label: string }[] = [];
  if (report.animalFilter) {
    animalId = sp.animal_id || undefined;
    const animals = await apiGetSafe<ApiRecord[]>('/reports/active-animals', []);
    animalOptions = animals.map((animal) => ({
      id: String(animal.animal_id),
      label: animal.name ? `${String(animal.tag_number)} - ${String(animal.name)}` : String(animal.tag_number),
    }));
  }

  const canFetch = !report.animalFilter || Boolean(animalId);
  let rows: ApiRecord[] = [];
  if (canFetch) {
    const query = new URLSearchParams();
    if (rangeStart) query.set('start_date', rangeStart);
    if (rangeEnd) query.set('end_date', rangeEnd);
    if (granularity) query.set('granularity', granularity);
    if (animalId) query.set('animal_id', animalId);
    const separator = report.endpoint.includes('?') ? '&' : '?';
    rows = await apiGetSafe<ApiRecord[]>(`${report.endpoint}${separator}${query.toString()}`, []);
  }

  const showCustomFilter = report.granularity || report.animalFilter;

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">{report.title}</h1>
      <p className="mb-4 text-sm text-slate-500">{report.description}</p>
      {showCustomFilter ? (
        <MarketValueSeriesFilter
          start={rangeStart}
          end={rangeEnd}
          granularity={granularity}
          animalId={animalId}
          animals={report.animalFilter ? animalOptions : undefined}
          showDateRange={Boolean(report.dateRange)}
          showGranularity={Boolean(report.granularity)}
          showAnimalPicker={Boolean(report.animalFilter)}
        />
      ) : (
        report.dateRange && rangeStart && rangeEnd && <DateRangeFilter start={rangeStart} end={rangeEnd} />
      )}
      {canFetch ? (
        <ReportTable report={report} rows={rows} />
      ) : (
        <p className="text-sm text-slate-500">Lütfen bir hayvan seçin.</p>
      )}
    </div>
  );
}
