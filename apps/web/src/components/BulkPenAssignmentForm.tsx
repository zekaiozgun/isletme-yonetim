'use client';

import { useMemo, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { bulkCreatePenAssignments, type BulkPenAssignmentResult } from '@/lib/actions';

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

/** BulkHealthEventForm ile aynı desen: hedef padok/tarih/neden TÜM seçili
 * hayvanlara birebir aynı uygulanır (bkz. lib/actions.ts
 * bulkCreatePenAssignments), satır başına tek şey değişir: hangi
 * hayvanların dahil olduğu (checkbox). Bir grup hayvanı (örn. sütten
 * kesim grubu) aynı anda yeni padoğa taşımak için kullanılır. */
export function BulkPenAssignmentForm({
  animals,
  pens,
  reasons,
}: {
  animals: AnimalOption[];
  pens: LookupOption[];
  reasons: LookupOption[];
}) {
  const router = useRouter();
  const [assignedDate, setAssignedDate] = useState(todayIso());
  const [penId, setPenId] = useState('');
  const [reasonId, setReasonId] = useState('');
  const [note, setNote] = useState('');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BulkPenAssignmentResult | null>(null);

  const filteredAnimals = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase('tr-TR');
    if (!needle) return animals;
    return animals.filter(
      (a) =>
        a.tagNumber.toLocaleLowerCase('tr-TR').includes(needle) ||
        (a.name ?? '').toLocaleLowerCase('tr-TR').includes(needle)
    );
  }, [animals, query]);

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleAllFiltered() {
    const allSelected = filteredAnimals.every((a) => selected.has(a.id));
    setSelected((prev) => {
      const next = new Set(prev);
      for (const a of filteredAnimals) {
        if (allSelected) next.delete(a.id);
        else next.add(a.id);
      }
      return next;
    });
  }

  function handleSubmit() {
    setError(null);
    setResult(null);

    if (!assignedDate) {
      setError('Tarih seçin.');
      return;
    }
    if (!penId) {
      setError('Hedef padok seçin.');
      return;
    }
    if (!reasonId) {
      setError('Neden seçin.');
      return;
    }
    if (selected.size === 0) {
      setError('En az bir hayvan seçin.');
      return;
    }

    const chosen = animals.filter((a) => selected.has(a.id)).map((a) => ({ animalId: a.id, tagNumber: a.tagNumber }));

    startTransition(async () => {
      const outcome = await bulkCreatePenAssignments(
        { penId: Number(penId), assignedDate, reasonId: Number(reasonId), note: note || null },
        chosen
      );
      if (outcome.failed.length === 0) {
        router.push('/pen-assignments');
        return;
      }
      setResult(outcome);
      setSelected((prev) => {
        const next = new Set(prev);
        for (const a of animals) {
          if (!outcome.failed.some((f) => f.tagNumber === a.tagNumber)) next.delete(a.id);
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
            Atama Tarihi <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={assignedDate}
            onChange={(e) => setAssignedDate(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Hedef Padok <span className="text-red-500">*</span>
          </label>
          <select
            value={penId}
            onChange={(e) => setPenId(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="" disabled>
              Seçiniz...
            </option>
            {pens.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Neden <span className="text-red-500">*</span>
          </label>
          <select
            value={reasonId}
            onChange={(e) => setReasonId(e.target.value)}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="" disabled>
              Seçiniz...
            </option>
            {reasons.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
        <div className="min-w-[12rem]">
          <label className="mb-1 block text-sm font-medium text-slate-700">Not</label>
          <input
            type="text"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div className="ml-auto text-sm text-slate-500">{selected.size} hayvan seçildi</div>
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
              <th className="px-3 py-2 text-left">
                <input
                  type="checkbox"
                  checked={filteredAnimals.length > 0 && filteredAnimals.every((a) => selected.has(a.id))}
                  onChange={toggleAllFiltered}
                  aria-label="Görünenlerin tümünü seç"
                />
              </th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Küpe No</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">İsim</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredAnimals.map((a) => (
              <tr key={a.id} className={selected.has(a.id) ? 'bg-blue-50' : undefined}>
                <td className="whitespace-nowrap px-3 py-2">
                  <input
                    type="checkbox"
                    checked={selected.has(a.id)}
                    onChange={() => toggle(a.id)}
                    aria-label={`${a.tagNumber} seç`}
                  />
                </td>
                <td className="whitespace-nowrap px-3 py-2 text-slate-700">{a.tagNumber}</td>
                <td className="whitespace-nowrap px-3 py-2 text-slate-500">{a.name ?? '—'}</td>
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
        {isPending ? 'Kaydediliyor...' : `Kaydet (${selected.size})`}
      </button>
    </div>
  );
}
