export function MarketValueSeriesFilter({
  start,
  end,
  asOfDate,
  granularity,
  showDateRange,
  showSingleDate,
  showGranularity,
}: {
  start?: string;
  end?: string;
  asOfDate?: string;
  granularity?: string;
  showDateRange: boolean;
  showSingleDate?: boolean;
  showGranularity: boolean;
}) {
  return (
    <form method="get" className="mb-4 flex flex-wrap items-end gap-3 rounded border border-slate-200 bg-slate-50 p-3">
      {showDateRange && (
        <>
          <div>
            <label htmlFor="start" className="mb-1 block text-xs font-medium text-slate-600">
              Başlangıç
            </label>
            <input
              type="date"
              id="start"
              name="start"
              defaultValue={start}
              className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
            />
          </div>
          <div>
            <label htmlFor="end" className="mb-1 block text-xs font-medium text-slate-600">
              Bitiş
            </label>
            <input
              type="date"
              id="end"
              name="end"
              defaultValue={end}
              className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
            />
          </div>
        </>
      )}
      {showSingleDate && (
        <div>
          <label htmlFor="as_of_date" className="mb-1 block text-xs font-medium text-slate-600">
            Tarih İtibarıyla
          </label>
          <input
            type="date"
            id="as_of_date"
            name="as_of_date"
            defaultValue={asOfDate}
            className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
          />
        </div>
      )}
      {showGranularity && (
        <div>
          <label htmlFor="granularity" className="mb-1 block text-xs font-medium text-slate-600">
            Granülerlik
          </label>
          <select
            id="granularity"
            name="granularity"
            defaultValue={granularity ?? 'monthly'}
            className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
          >
            <option value="daily">Günlük</option>
            <option value="weekly">Haftalık</option>
            <option value="monthly">Aylık</option>
          </select>
        </div>
      )}
      <button type="submit" className="rounded bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700">
        Filtrele
      </button>
    </form>
  );
}
