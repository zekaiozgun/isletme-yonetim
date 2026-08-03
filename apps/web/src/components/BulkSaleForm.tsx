'use client';

import { useMemo, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { bulkCreateSales, type BulkSaleResult } from '@/lib/actions';

interface AnimalOption {
  id: string;
  tagNumber: string;
  name?: string;
}

interface LookupOption {
  id: number;
  name: string;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

/** BulkWeightForm ile aynı desen (alıcı/tarih/satış tipi bir kez seçilir)
 * ama satır başına ÜÇ değer var: canlı ağırlık, karkas ağırlığı (ikisi de
 * opsiyonel - karkas sadece kesim satışlarında anlamlı) ve tutar (zorunlu)
 * - aynı gün aynı alıcıya birden fazla hayvan satıldığında kullanılır (bkz.
 * lib/actions.ts bulkCreateSales). */
export function BulkSaleForm({
  animals,
  buyers,
  saleTypes,
}: {
  animals: AnimalOption[];
  buyers: LookupOption[];
  saleTypes: LookupOption[];
}) {
  const router = useRouter();
  const [saleDate, setSaleDate] = useState(todayIso());
  const [buyerId, setBuyerId] = useState('');
  const [saleTypeId, setSaleTypeId] = useState('');
  const [weights, setWeights] = useState<Record<string, string>>({});
  const [carcassWeights, setCarcassWeights] = useState<Record<string, string>>({});
  const [amounts, setAmounts] = useState<Record<string, string>>({});
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BulkSaleResult | null>(null);

  const filteredAnimals = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase('tr-TR');
    if (!needle) return animals;
    return animals.filter(
      (a) =>
        a.tagNumber.toLocaleLowerCase('tr-TR').includes(needle) ||
        (a.name ?? '').toLocaleLowerCase('tr-TR').includes(needle)
    );
  }, [animals, query]);

  const filledCount = useMemo(() => Object.values(amounts).filter((v) => v.trim() !== '').length, [amounts]);

  function handleSubmit() {
    setError(null);
    setResult(null);

    if (!saleDate) {
      setError('Tarih seçin.');
      return;
    }
    if (!buyerId) {
      setError('Alıcı seçin.');
      return;
    }
    if (!saleTypeId) {
      setError('Satış tipi seçin.');
      return;
    }

    const entries = animals
      .filter((a) => amounts[a.id]?.trim())
      .map((a) => ({
        animalId: a.id,
        tagNumber: a.tagNumber,
        saleWeightKg: weights[a.id]?.trim() ? Number(weights[a.id]) : null,
        carcassWeightKg: carcassWeights[a.id]?.trim() ? Number(carcassWeights[a.id]) : null,
        totalAmount: Number(amounts[a.id]),
      }));

    if (entries.length === 0) {
      setError('En az bir hayvana tutar girin.');
      return;
    }
    if (entries.some((e) => Number.isNaN(e.totalAmount) || e.totalAmount <= 0)) {
      setError('Girilen tutar değerleri geçerli bir sayı olmalı.');
      return;
    }
    if (entries.some((e) => e.saleWeightKg !== null && (Number.isNaN(e.saleWeightKg) || e.saleWeightKg <= 0))) {
      setError('Girilen canlı ağırlık değerleri geçerli bir sayı olmalı.');
      return;
    }
    if (
      entries.some((e) => e.carcassWeightKg !== null && (Number.isNaN(e.carcassWeightKg) || e.carcassWeightKg <= 0))
    ) {
      setError('Girilen karkas ağırlığı değerleri geçerli bir sayı olmalı.');
      return;
    }

    startTransition(async () => {
      const outcome = await bulkCreateSales(saleDate, Number(buyerId), Number(saleTypeId), entries);
      if (outcome.failed.length === 0) {
        router.push('/sales');
        return;
      }
      setResult(outcome);
      // Basariyla kaydedilenleri temizle, sadece basarisizlar formda kalsin.
      setAmounts((prev) => {
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
            value={saleDate}
            onChange={(e) => setSaleDate(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Alıcı <span className="text-red-500">*</span>
          </label>
          <select
            value={buyerId}
            onChange={(e) => setBuyerId(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="" disabled>
              Seçiniz...
            </option>
            {buyers.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Satış Tipi <span className="text-red-500">*</span>
          </label>
          <select
            value={saleTypeId}
            onChange={(e) => setSaleTypeId(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="" disabled>
              Seçiniz...
            </option>
            {saleTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
        <div className="ml-auto text-sm text-slate-500">{filledCount} hayvan için tutar girildi</div>
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
              <th className="px-3 py-2 text-left font-medium text-slate-600">Canlı Ağırlık (kg)</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Karkas Ağırlığı (kg)</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Tutar (TL)</th>
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
                <td className="px-3 py-2">
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={carcassWeights[a.id] ?? ''}
                    onChange={(e) => setCarcassWeights((prev) => ({ ...prev, [a.id]: e.target.value }))}
                    className="w-28 rounded border border-slate-300 px-2 py-1 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={amounts[a.id] ?? ''}
                    onChange={(e) => setAmounts((prev) => ({ ...prev, [a.id]: e.target.value }))}
                    className="w-28 rounded border border-slate-300 px-2 py-1 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
                  />
                </td>
              </tr>
            ))}
            {filteredAnimals.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-center text-slate-500">
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
