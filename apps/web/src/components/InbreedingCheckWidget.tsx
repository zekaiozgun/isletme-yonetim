'use client';

import { useState, useTransition } from 'react';
import { checkInbreedingAction } from '@/lib/actions';

interface Option {
  value: string;
  label: string;
}

/** Aşım Kaydı formunun ÜSTÜNDE, formu değiştirmeden duran bağımsız bir
 * yardımcı araç - anne adayı ile prospektif boğanın (doğal aşım ya da
 * suni tohumlama) soy ağaçlarında ortak bir ata olup olmadığını kontrol
 * eder (bkz. app/modules/breeding/service.py check_inbreeding). Sistem
 * HİÇBİR ŞEYİ ENGELLEMEZ - sadece kullanıcıyı bilgilendirir, karar
 * kullanıcıya aittir (kullanıcıyla üzerinde anlaşılan Faz 4 kural seti). */
export function InbreedingCheckWidget({
  animals,
  sireAnimals,
  semenBatches,
}: {
  animals: Option[];
  sireAnimals: Option[];
  semenBatches: Option[];
}) {
  const [damId, setDamId] = useState('');
  const [sireAnimalId, setSireAnimalId] = useState('');
  const [semenBatchId, setSemenBatchId] = useState('');
  const [result, setResult] = useState<{ hasCommonAncestor: boolean; commonAncestorNames: string[] } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function handleCheck() {
    setError(null);
    setResult(null);
    if (!damId) {
      setError('Önce anne adayını seçin.');
      return;
    }
    if (!sireAnimalId && !semenBatchId) {
      setError('Boğa (doğal aşım) ya da sperma partisi (suni tohumlama) seçin.');
      return;
    }
    startTransition(async () => {
      const outcome = await checkInbreedingAction(
        damId,
        sireAnimalId || null,
        semenBatchId ? Number(semenBatchId) : null
      );
      if (outcome.error !== undefined) {
        setError(outcome.error);
        return;
      }
      setResult(outcome.data!);
    });
  }

  return (
    <div className="mb-4 rounded border border-slate-200 bg-slate-50 p-3">
      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">Akrabalık Kontrolü</p>
      <div className="mb-2 grid grid-cols-1 gap-2 sm:grid-cols-3">
        <select
          value={damId}
          onChange={(e) => setDamId(e.target.value)}
          className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
        >
          <option value="">Anne Adayı</option>
          {animals.map((a) => (
            <option key={a.value} value={a.value}>
              {a.label}
            </option>
          ))}
        </select>
        <select
          value={sireAnimalId}
          onChange={(e) => {
            setSireAnimalId(e.target.value);
            if (e.target.value) setSemenBatchId('');
          }}
          className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
        >
          <option value="">Boğa (Doğal Aşım)</option>
          {sireAnimals.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
        <select
          value={semenBatchId}
          onChange={(e) => {
            setSemenBatchId(e.target.value);
            if (e.target.value) setSireAnimalId('');
          }}
          className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
        >
          <option value="">Sperma Partisi (Suni Tohumlama)</option>
          {semenBatches.map((b) => (
            <option key={b.value} value={b.value}>
              {b.label}
            </option>
          ))}
        </select>
      </div>
      <button
        type="button"
        onClick={handleCheck}
        disabled={isPending}
        className="rounded border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
      >
        {isPending ? 'Kontrol Ediliyor...' : 'Kontrol Et'}
      </button>
      {error && <p className="mt-2 text-sm text-red-700">{error}</p>}
      {result && (
        <div className="mt-2 text-sm">
          {result.hasCommonAncestor ? (
            <p className="font-medium text-amber-800">
              ⚠ Ortak ata bulundu: {result.commonAncestorNames.join(', ')} — yakın akrabalık olabilir.
            </p>
          ) : (
            <p className="font-medium text-emerald-700">Son 4 nesilde ortak ata bulunamadı.</p>
          )}
        </div>
      )}
    </div>
  );
}
