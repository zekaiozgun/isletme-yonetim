interface AnimalOption {
  id: string;
  label: string;
}

/**
 * Tartılar listesini tek bir hayvana daraltan basit bir GET formu -
 * DateRangeFilter/MarketValueSeriesFilter ile aynı desen (native form
 * navigasyonu, ayrı bir client bileşeni/JS gerekmez). Seçim yapılınca
 * sayfa `?animal_id=` ile yeniden yüklenir; page.tsx o hayvanın kilo
 * trend grafiğini listenin üstünde gösterir.
 */
export function WeightAnimalFilter({ animals, selectedId }: { animals: AnimalOption[]; selectedId?: string }) {
  return (
    <form method="get" className="mb-4 flex flex-wrap items-end gap-3 rounded border border-slate-200 bg-slate-50 p-3 print:hidden">
      <div>
        <label htmlFor="animal_id" className="mb-1 block text-xs font-medium text-slate-600">
          Hayvana Göre Filtrele (Kilo Trend Grafiği İçin)
        </label>
        <select
          id="animal_id"
          name="animal_id"
          defaultValue={selectedId ?? ''}
          className="min-w-[220px] rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
        >
          <option value="">Tüm hayvanlar</option>
          {animals.map((a) => (
            <option key={a.id} value={a.id}>
              {a.label}
            </option>
          ))}
        </select>
      </div>
      <button type="submit" className="rounded bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700">
        Filtrele
      </button>
    </form>
  );
}
