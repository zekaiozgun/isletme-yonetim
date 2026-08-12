'use client';

import { useMemo, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { bulkCreateHealthEvents, type BulkHealthEventResult, type HealthEventMedicationInput } from '@/lib/actions';

interface AnimalOption {
  id: string;
  tagNumber: string;
  name?: string;
}

interface LookupOption {
  id: number;
  name: string;
}

interface MedicationRow {
  key: number;
  medicationId: string;
  dosageAmount: string;
  dosageUnitId: string;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function emptyRow(key: number): MedicationRow {
  return { key, medicationId: '', dosageAmount: '', dosageUnitId: '' };
}

/** Diğer toplu giriş formlarından farklı desen: burada hayvana özel bir
 * DEĞER yok (kilo/sonuç gibi) - aynı aşı/ilaç turu TÜM seçili hayvanlara
 * BİREBİR AYNI bilgiyle uygulanır (bkz. lib/actions.ts
 * bulkCreateHealthEvents dokümantasyonu). Satır başına tek şey değişir:
 * hangi hayvanların dahil olduğu (checkbox). */
export function BulkHealthEventForm({
  animals,
  eventTypes,
  diseases,
  medications,
  dosageUnits,
}: {
  animals: AnimalOption[];
  eventTypes: LookupOption[];
  diseases: LookupOption[];
  medications: LookupOption[];
  dosageUnits: LookupOption[];
}) {
  const router = useRouter();
  const [eventDate, setEventDate] = useState(todayIso());
  const [eventTypeId, setEventTypeId] = useState('');
  const [diseaseId, setDiseaseId] = useState('');
  const [rows, setRows] = useState<MedicationRow[]>([]);
  const [nextKey, setNextKey] = useState(0);
  const [veterinarianNote, setVeterinarianNote] = useState('');
  const [cost, setCost] = useState('');
  const [note, setNote] = useState('');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BulkHealthEventResult | null>(null);

  function updateRow(key: number, patch: Partial<MedicationRow>) {
    setRows((prev) => prev.map((row) => (row.key === key ? { ...row, ...patch } : row)));
  }

  function addRow() {
    setRows((prev) => [...prev, emptyRow(nextKey)]);
    setNextKey((k) => k + 1);
  }

  function removeRow(key: number) {
    setRows((prev) => prev.filter((row) => row.key !== key));
  }

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

    if (!eventDate) {
      setError('Tarih seçin.');
      return;
    }
    if (!eventTypeId) {
      setError('Olay tipi seçin.');
      return;
    }
    if (selected.size === 0) {
      setError('En az bir hayvan seçin.');
      return;
    }

    const chosen = animals.filter((a) => selected.has(a.id)).map((a) => ({ animalId: a.id, tagNumber: a.tagNumber }));
    const medications: HealthEventMedicationInput[] = rows
      .filter((row) => row.medicationId)
      .map((row) => ({
        medicationId: Number(row.medicationId),
        dosageAmount: row.dosageAmount ? Number(row.dosageAmount) : null,
        dosageUnitId: row.dosageUnitId ? Number(row.dosageUnitId) : null,
      }));

    startTransition(async () => {
      const outcome = await bulkCreateHealthEvents(
        {
          eventTypeId: Number(eventTypeId),
          eventDate,
          diseaseId: diseaseId ? Number(diseaseId) : null,
          medications,
          veterinarianNote: veterinarianNote || null,
          cost: cost ? Number(cost) : null,
          note: note || null,
        },
        chosen
      );
      if (outcome.failed.length === 0) {
        router.push('/health-events');
        return;
      }
      setResult(outcome);
      // Basariyla kaydedilenlerin secimini kaldir, sadece basarisizlar secili kalsin.
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
      <div className="grid grid-cols-1 gap-4 rounded border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Tarih <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={eventDate}
            onChange={(e) => setEventDate(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Olay Tipi <span className="text-red-500">*</span>
          </label>
          <select
            value={eventTypeId}
            onChange={(e) => setEventTypeId(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="" disabled>
              Seçiniz...
            </option>
            {eventTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Hastalık/Tanı</label>
          <select
            value={diseaseId}
            onChange={(e) => setDiseaseId(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="">—</option>
            {diseases.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
        <div className="sm:col-span-2 lg:col-span-3">
          <div className="mb-2 flex items-center justify-between">
            <label className="block text-sm font-medium text-slate-700">İlaçlar</label>
            <span className="text-xs text-slate-400">Seçili tüm hayvanlara aynı ilaçlar uygulanır</span>
          </div>
          <div className="space-y-2">
            {rows.map((row) => (
              <div key={row.key} className="flex flex-wrap items-center gap-2 rounded border border-slate-200 bg-white p-2">
                <select
                  value={row.medicationId}
                  onChange={(e) => updateRow(row.key, { medicationId: e.target.value })}
                  className="flex-1 rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
                >
                  <option value="">İlaç seçin...</option>
                  {medications.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="Doz"
                  value={row.dosageAmount}
                  onChange={(e) => updateRow(row.key, { dosageAmount: e.target.value })}
                  className="w-24 rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
                />
                <select
                  value={row.dosageUnitId}
                  onChange={(e) => updateRow(row.key, { dosageUnitId: e.target.value })}
                  className="w-28 rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
                >
                  <option value="">Birim</option>
                  {dosageUnits.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={() => removeRow(row.key)}
                  className="rounded px-2 py-1.5 text-sm text-slate-400 hover:bg-slate-100 hover:text-red-600"
                  aria-label="İlacı kaldır"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={addRow}
            className="mt-2 rounded border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            + İlaç Ekle
          </button>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Maliyet (TL, hayvan başına)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={cost}
            onChange={(e) => setCost(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div className="sm:col-span-2 lg:col-span-3">
          <label className="mb-1 block text-sm font-medium text-slate-700">Veteriner Notu</label>
          <textarea
            value={veterinarianNote}
            onChange={(e) => setVeterinarianNote(e.target.value)}
            rows={2}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div className="sm:col-span-2 lg:col-span-3">
          <label className="mb-1 block text-sm font-medium text-slate-700">Not</label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={2}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div className="text-sm text-slate-500 sm:col-span-2 lg:col-span-3">{selected.size} hayvan seçildi</div>
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
