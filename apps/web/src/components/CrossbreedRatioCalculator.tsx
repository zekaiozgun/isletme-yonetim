'use client';

import { useState, useTransition } from 'react';
import { estimateCrossbreedRatioAction } from '@/lib/actions';

interface Option {
  value: string;
  label: string;
}

function formatRatio(ratio: number | null): string {
  if (ratio === null) return '—';
  const rounded = Math.round(ratio * 100) / 100;
  return `%${rounded}`;
}

/** Yeni Hayvan formunun ÜSTÜNDE, formu değiştirmeden duran bağımsız bir
 * yardımcı araç - anne/baba/hedef ırk seçilince beklenen melez oranını
 * hesaplar (bkz. app/modules/animal/service.py estimate_crossbreed_ratio,
 * kullanıcıyla üzerinde anlaşılan kural seti). Sonuç, aşağıdaki gerçek
 * "Melez Oranı (%)" alanına tek tıkla yazılabilir - ama HER ZAMAN elle
 * değiştirilebilir kalır, sessizce üzerine yazılmaz. */
export function CrossbreedRatioCalculator({
  animals,
  sires,
  breeds,
}: {
  animals: Option[];
  sires: Option[];
  breeds: Option[];
}) {
  const [motherId, setMotherId] = useState('');
  const [sireId, setSireId] = useState('');
  const [breedId, setBreedId] = useState('');
  const [result, setResult] = useState<{ ratio: number | null; note: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function handleCalculate() {
    setError(null);
    setResult(null);
    if (!breedId) {
      setError('Önce hedef ırkı seçin.');
      return;
    }
    startTransition(async () => {
      const outcome = await estimateCrossbreedRatioAction(
        Number(breedId),
        motherId || null,
        sireId ? Number(sireId) : null
      );
      if (outcome.error !== undefined) {
        setError(outcome.error);
        return;
      }
      setResult({ ratio: outcome.data!.ratio, note: outcome.data!.note });
    });
  }

  function handleApply() {
    if (result === null || result.ratio === null) return;
    const input = document.getElementById('crossbreed_ratio') as HTMLInputElement | null;
    if (input) input.value = String(Math.round(result.ratio * 100) / 100);
  }

  return (
    <div className="mb-4 rounded border border-slate-200 bg-slate-50 p-3">
      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">Melez Oranı Hesaplayıcı</p>
      <div className="mb-2 grid grid-cols-1 gap-2 sm:grid-cols-3">
        <select
          value={motherId}
          onChange={(e) => setMotherId(e.target.value)}
          className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
        >
          <option value="">Anne (opsiyonel)</option>
          {animals.map((a) => (
            <option key={a.value} value={a.value}>
              {a.label}
            </option>
          ))}
        </select>
        <select
          value={sireId}
          onChange={(e) => setSireId(e.target.value)}
          className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
        >
          <option value="">Baba (opsiyonel)</option>
          {sires.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
        <select
          value={breedId}
          onChange={(e) => setBreedId(e.target.value)}
          className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
        >
          <option value="">Hedef ırk seçin...</option>
          {breeds.map((b) => (
            <option key={b.value} value={b.value}>
              {b.label}
            </option>
          ))}
        </select>
      </div>
      <button
        type="button"
        onClick={handleCalculate}
        disabled={isPending}
        className="rounded border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
      >
        {isPending ? 'Hesaplanıyor...' : 'Hesapla'}
      </button>
      {error && <p className="mt-2 text-sm text-red-700">{error}</p>}
      {result && (
        <div className="mt-2 text-sm">
          <p className="font-medium text-slate-800">
            Önerilen oran: <span className="tabular-nums">{formatRatio(result.ratio)}</span>
          </p>
          <p className="text-xs text-slate-500">{result.note}</p>
          {result.ratio !== null && (
            <button
              type="button"
              onClick={handleApply}
              className="mt-1 text-xs font-medium text-slate-700 hover:underline"
            >
              Bu değeri "Melez Oranı (%)" alanına yaz →
            </button>
          )}
        </div>
      )}
    </div>
  );
}
