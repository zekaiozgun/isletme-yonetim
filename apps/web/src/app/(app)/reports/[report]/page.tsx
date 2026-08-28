import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGet, apiGetSafe, type ApiRecord } from '@/lib/api';
import { getReport } from '@/lib/reports';
import { ReportTable } from '@/components/ReportTable';
import { HerdAnimalValueTable } from '@/components/HerdAnimalValueTable';
import { HerdProfitLossSection } from '@/components/HerdProfitLossSection';
import { ParentPerformanceSection } from '@/components/ParentPerformanceSection';
import { DailyFeedCostSection } from '@/components/DailyFeedCostSection';
import { GroupedOffspringList } from '@/components/GroupedOffspringList';
import { DateRangeFilter } from '@/components/DateRangeFilter';
import { MarketValueSeriesFilter } from '@/components/MarketValueSeriesFilter';
import { formatNowIstanbulDMYHM } from '@/lib/format';

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function firstDayOfMonthIso(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
}

function daysAgoIso(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
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
    filtered?: string;
    status_ids?: string | string[];
    q?: string;
  }>;
}) {
  const { report: slug } = await params;
  const report = getReport(slug);
  if (!report) notFound();

  const sp = await searchParams;

  let rangeStart: string | undefined;
  let rangeEnd: string | undefined;
  if (report.dateRange) {
    rangeStart = sp.start || (report.defaultRangeDays ? daysAgoIso(report.defaultRangeDays) : firstDayOfMonthIso());
    rangeEnd = sp.end || todayIso();
  }

  const asOfDate = report.singleDate ? sp.as_of_date || todayIso() : undefined;

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

  const searchQuery = report.serverSearch ? (sp.q ?? '').trim() : undefined;

  const query = new URLSearchParams();
  if (rangeStart) query.set('start_date', rangeStart);
  if (rangeEnd) query.set('end_date', rangeEnd);
  if (asOfDate) query.set('as_of_date', asOfDate);
  for (const id of selectedStatusIds) query.append('status_ids', String(id));
  if (searchQuery) query.set('q', searchQuery);
  const separator = report.endpoint.includes('?') ? '&' : '?';
  // Bilerek apiGetSafe DEĞİL, apiGet: rapor verisi çekilemezse (backend'e
  // ulaşılamıyor) bunu "veri bulunamadı" gibi göstermek yanıltıcı olurdu -
  // hata (app/error.tsx) sınırına düşüp gerçek durumu ("Sunucuya şu anda
  // ulaşılamıyor") göstersin (bkz. kullanıcı geri bildirimi - 2026-08-28
  // olayı: bağlantı sorunu boş veriyle karıştırılmıştı).
  const rows = await apiGet<ApiRecord[]>(`${report.endpoint}${separator}${query.toString()}`);
  const sireRows =
    report.slug === 'parent-performance' ? await apiGetSafe<ApiRecord[]>('/reports/sire-performance', []) : [];
  const feedStockRunwayRows =
    report.slug === 'feed-daily-cost'
      ? await apiGetSafe<ApiRecord[]>(`/reports/feed-stock-runway${separator}${query.toString()}`, [])
      : [];

  const showCustomFilter = report.singleDate || report.statusFilter;

  return (
    <div>
      <div className="mb-1 flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
        <h1 className="text-xl font-semibold text-slate-900">{report.title}</h1>
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
          {report.usesGrowthCheckpoints && (
            <Link
              href="/growth-valuation-checkpoints"
              className="text-sm font-medium text-slate-500 hover:text-slate-800 hover:underline print:hidden"
            >
              Büyüme Değerleme Çıpalarını Düzenle →
            </Link>
          )}
          <span className="whitespace-nowrap text-xs text-slate-400">Oluşturulma: {formatNowIstanbulDMYHM()}</span>
        </div>
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
          statuses={report.statusFilter ? statusOptions : undefined}
          selectedStatusIds={report.statusFilter ? selectedStatusIds : undefined}
          showDateRange={Boolean(report.dateRange)}
          showSingleDate={Boolean(report.singleDate)}
          showStatusFilter={Boolean(report.statusFilter)}
        />
      ) : (
        report.dateRange && rangeStart && rangeEnd && <DateRangeFilter start={rangeStart} end={rangeEnd} />
      )}
      {report.slug === 'herd-animal-market-values' ? (
        <HerdAnimalValueTable rows={rows} asOfDate={asOfDate} />
      ) : report.slug === 'herd-profit-loss' ? (
        rows[0] ? <HerdProfitLossSection data={rows[0]} /> : <p className="text-sm text-slate-500">Bu tarih aralığında veri bulunamadı.</p>
      ) : report.slug === 'parent-performance' ? (
        <ParentPerformanceSection motherRows={rows} sireRows={sireRows} />
      ) : report.slug === 'feed-daily-cost' ? (
        <DailyFeedCostSection costReport={report} costRows={rows} runwayRows={feedStockRunwayRows} />
      ) : report.groupBy ? (
        <GroupedOffspringList report={report} rows={rows} searchQuery={searchQuery} />
      ) : (
        <ReportTable report={report} rows={rows} serverQuery={searchQuery} />
      )}
    </div>
  );
}
