'use client';

import { useMemo, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { bulkCreateWeightRecords, type BulkWeightResult } from '@/lib/actions';

interface AnimalOption {
  id: string;
  tagNumber: string;
  name?: string;
}

interface MethodOption {
  id: number;
  name: string;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function BulkWeightForm({ animals, weighingMethods }: { animals: AnimalOption[]; weighingMethods: MethodOption[] }) {
  const router = useRouter();
  const [weighDate, setWeighDate] = useState(todayIso());
  const [weighingMethodId, setWeighingMethodId] = useState('');
  const [weights, setWeights] = useState<Record<string, string>>({});
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BulkWeightResult | null>(null);

  const filteredAnimals = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase('tr-TR');
    if (!needle) return animals;
    return animals.filter(
      (a) =>
        a.tagNumber.toLocaleLowerCase('tr-TR').includes(needle) ||
        (a.name ?? '').toLocaleLowerCase('tr-TR').includes(needle)
    );
  }, [animals, query]);

  const filledCount = useMemo(() => Object.values(weights).filter((v) => v.trim() !== '').length, [weights]);

  function handleSubmit() {
    setError(null);
    setResult(null);

    if (!weighDate) {
      setError('Tarih seçin.');
      return;
    }
    if (!weighingMethodId) {
      setError('Tartı yöntemi seçin.');
      return;
    }

    const entries = animals
      .filter((a) => weights[a.id]?.trim())
      .map((a) => ({ animalId: a.id, tagNumber: a.tagNumber, weightKg: Number(weights[a.id]) }));

    if (entries.length === 0) {
      setError('En az bir hayvana kilo girin.');
      return;
    }
    if (entries.some((e) => Number.isNaN(e.weightKg) || e.weightKg <= 0)) {
      setError('Girilen kilo değerleri geçerli bir sayı olmalı.');
      return;
    }

    startTransition(async () => {
      const outcome = await bulkCreateWeightRecords(weighDate, Number(weighingMethodId), entries);
      if (outcome.failed.length === 0) {
        router.push('/weight-records');
        return;
      }
      setResult(outcome);
      // Basariyla kaydedilenleri temizle, sadece basarisizlar formda kalsin.
      setWeights((prev) => {
        const next = { ...prev };
        for (const a of animals) {
          if (!outcome.failed.some((f) => f.tagNumber === a.tagNumber)) delete next[a.id];
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
            Tarih <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={weighDate}
            onChange={(e) => setWeighDate(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Tartı Yöntemi <span className="text-red-500">*</span>
          </label>
          <select
            value={weighingMethodId}
            onChange={(e) => setWeighingMethodId(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="" disabled>
              Seçiniz...
            </option>
            {weighingMethods.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>
        <div className="ml-auto text-sm text-slate-500">{filledCount} hayvan için kilo girildi</div>
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
        placeholder="Küpe no veya isimle ara..."
        className="w-full max-w-sm rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
      />

      <div className="overflow-x-auto rounded border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Küpe No</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">İsim</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Kilo (kg)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredAnimals.map((a) => (
              <tr key={a.id}>
                <td className="whitespace-nowrap px-3 py-2 text-slate-700">{a.tagNumber}</td>
                <td className="whitespace-nowrap px-3 py-2 text-slate-500">{a.name ?? '—'}</td>
                <td className="px-3 py-2">
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={weights[a.id] ?? ''}
                    onChange={(e) => setWeights((prev) => ({ ...prev, [a.id]: e.target.value }))}
                    className="w-28 rounded border border-slate-300 px-2 py-1 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
                  />
                </td>
              </tr>
            ))}
            {filteredAnimals.length === 0 && (
              <tr>
                <td colSpan={3} className="px-3 py-4 text-center text-slate-500">
                  Aramanızla eşleşen aktif hayvan yok.
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
