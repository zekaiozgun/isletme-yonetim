interface StatusOption {
  id: number;
  name: string;
}

export function MarketValueSeriesFilter({
  start,
  end,
  asOfDate,
  granularity,
  statuses,
  selectedStatusIds,
  showDateRange,
  showSingleDate,
  showGranularity,
  showStatusFilter,
}: {
  start?: string;
  end?: string;
  asOfDate?: string;
  granularity?: string;
  statuses?: StatusOption[];
  selectedStatusIds?: number[];
  showDateRange: boolean;
  showSingleDate?: boolean;
  showGranularity: boolean;
  showStatusFilter?: boolean;
}) {
  return (
    <form method="get" className="mb-4 flex flex-wrap items-end gap-3 rounded border border-slate-200 bg-slate-50 p-3 print:hidden">
      {showStatusFilter && (
        <div>
          <input type="hidden" name="filtered" value="1" />
          <span className="mb-1 block text-xs font-medium text-slate-600">Statü</span>
          <div className="flex flex-wrap gap-3 py-1">
            {(statuses ?? []).map((status) => (
              <label key={status.id} className="flex items-center gap-1.5 text-sm text-slate-700">
                <input
                  type="checkbox"
                  name="status_ids"
                  value={status.id}
                  defaultChecked={(selectedStatusIds ?? []).includes(status.id)}
                />
                {status.name}
              </label>
            ))}
          </div>
        </div>
      )}
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
