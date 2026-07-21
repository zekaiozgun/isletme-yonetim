export function DateRangeFilter({ start, end }: { start: string; end: string }) {
  return (
    <form method="get" className="mb-4 flex flex-wrap items-end gap-3 rounded border border-slate-200 bg-slate-50 p-3">
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
      <button type="submit" className="rounded bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700">
        Filtrele
      </button>
    </form>
  );
}
