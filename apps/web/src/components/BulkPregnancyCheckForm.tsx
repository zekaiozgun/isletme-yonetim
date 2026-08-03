'use client';

import { useMemo, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { bulkCreatePregnancyChecks, type BulkPregnancyCheckResult } from '@/lib/actions';
import { formatDateDMY } from '@/lib/format';

interface PendingBreedingEvent {
  id: number;
  tagNumber: string;
  serviceDate: string;
}

interface ResultOption {
  id: number;
  name: string;
}

interface MethodOption {
  id: number;
  name: string;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

/** Toplu tartı girişiyle (BulkWeightForm) aynı desen: tarih/yöntem bir kez
 * seçilir, sadece kontrolünü yaptığınız hayvanlara sonuç seçilir - boş
 * bırakılanlar kaydedilmez. Satırlar hayvan değil TOHUMLAMA KAYDI bazlıdır
 * (breeding_event_id) çünkü bir gebelik kontrolü doğrudan hayvana değil,
 * belirli bir aşım kaydına bağlanır (bkz. resources.ts pregnancy-checks). */
export function BulkPregnancyCheckForm({
  pendingEvents,
  methods,
  results,
}: {
  pendingEvents: PendingBreedingEvent[];
  methods: MethodOption[];
  results: ResultOption[];
}) {
  const router = useRouter();
  const [checkDate, setCheckDate] = useState(todayIso());
  const [methodId, setMethodId] = useState('');
  const [selectedResults, setSelectedResults] = useState<Record<number, string>>({});
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BulkPregnancyCheckResult | null>(null);

  const filteredEvents = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase('tr-TR');
    if (!needle) return pendingEvents;
    return pendingEvents.filter((e) => e.tagNumber.toLocaleLowerCase('tr-TR').includes(needle));
  }, [pendingEvents, query]);

  const filledCount = useMemo(
    () => Object.values(selectedResults).filter((v) => v.trim() !== '').length,
    [selectedResults]
  );

  function handleSubmit() {
    setError(null);
    setResult(null);

    if (!checkDate) {
      setError('Tarih seçin.');
      return;
    }
    if (!methodId) {
      setError('Kontrol yöntemi seçin.');
      return;
    }

    const entries = pendingEvents
      .filter((e) => selectedResults[e.id]?.trim())
      .map((e) => ({ breedingEventId: e.id, tagNumber: e.tagNumber, resultId: Number(selectedResults[e.id]) }));

    if (entries.length === 0) {
      setError('En az bir hayvana sonuç girin.');
      return;
    }

    startTransition(async () => {
      const outcome = await bulkCreatePregnancyChecks(checkDate, Number(methodId), entries);
      if (outcome.failed.length === 0) {
        router.push('/pregnancy-checks');
        return;
      }
      setResult(outcome);
      // Basariyla kaydedilenleri temizle, sadece basarisizlar formda kalsin.
      setSelectedResults((prev) => {
        const next = { ...prev };
        for (const e of pendingEvents) {
          if (!outcome.failed.some((f) => f.tagNumber === e.tagNumber)) delete next[e.id];
        }
        return next;
      });
    });
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-4 rounded border border-slate-200 bg-slate-50 p-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Kontrol Tarihi <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={checkDate}
            onChange={(e) => setCheckDate(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Kontrol Yöntemi <span className="text-red-500">*</span>
          </label>
          <select
            value={methodId}
            onChange={(e) => setMethodId(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="" disabled>
              Seçiniz...
            </option>
            {methods.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>
        <div className="ml-auto text-sm text-slate-500">{filledCount} hayvan için sonuç girildi</div>
      </div>

      {error && <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      {result && result.failed.length > 0 && (
        <div className="rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
          <p className="mb-1 font-medium">
            {result.success} kayıt başarıyla eklendi, {result.failed.length} tanesi başarısız oldu — aşağıda kalan
            satırları düzeltip tekrar deneyin:
          </p>
          <ul className="list-disc pl-5">
            {result.failed.map((f) => (
              <li key={f.tagNumber}>
                {f.tagNumber}: {f.error}
              </li>
            ))}
          </ul>
        </div>
      )}

      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Küpe no ile ara..."
        className="w-full max-w-sm rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
      />

      <div className="overflow-x-auto rounded border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Küpe No</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Tohumlama Tarihi</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Sonuç</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredEvents.map((e) => (
              <tr key={e.id}>
                <td className="whitespace-nowrap px-3 py-2 text-slate-700">{e.tagNumber}</td>
                <td className="whitespace-nowrap px-3 py-2 text-slate-500">{formatDateDMY(e.serviceDate)}</td>
                <td className="px-3 py-2">
                  <select
                    value={selectedResults[e.id] ?? ''}
                    onChange={(ev) => setSelectedResults((prev) => ({ ...prev, [e.id]: ev.target.value }))}
                    className="w-40 rounded border border-slate-300 px-2 py-1 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
                  >
                    <option value="">—</option>
                    {results.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
            {filteredEvents.length === 0 && (
              <tr>
                <td colSpan={3} className="px-3 py-4 text-center text-slate-500">
                  Kontrol bekleyen tohumlama kaydı yok.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <button
        type="button"
        onClick={handleSubmit}
        disabled={isPending}
        className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {isPending ? 'Kaydediliyor...' : `Kaydet (${filledCount})`}
      </button>
    </div>
  );
}
