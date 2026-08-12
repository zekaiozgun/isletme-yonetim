'use client';

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import {
  createHealthEventAction,
  updateHealthEventAction,
  type HealthEventMedicationInput,
} from '@/lib/actions';

interface AnimalOption {
  id: string;
  label: string;
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

export interface HealthEventFormInitial {
  animalId: string;
  eventTypeId: string;
  eventDate: string;
  diseaseId: string;
  veterinarianNote: string;
  cost: string;
  note: string;
  medications: { medicationId: string; dosageAmount: string; dosageUnitId: string }[];
}

export function HealthEventForm({
  animals,
  eventTypes,
  diseases,
  medications,
  dosageUnits,
  eventId,
  initial,
}: {
  animals: AnimalOption[];
  eventTypes: LookupOption[];
  diseases: LookupOption[];
  medications: LookupOption[];
  dosageUnits: LookupOption[];
  /** Belirtilirse form DÜZENLEME modunda çalışır (createHealthEventAction yerine
   * updateHealthEventAction çağrılır). */
  eventId?: string;
  initial?: HealthEventFormInitial;
}) {
  const router = useRouter();
  const [animalId, setAnimalId] = useState(initial?.animalId ?? '');
  const [eventTypeId, setEventTypeId] = useState(initial?.eventTypeId ?? '');
  const [eventDate, setEventDate] = useState(initial?.eventDate ?? todayIso());
  const [diseaseId, setDiseaseId] = useState(initial?.diseaseId ?? '');
  const [veterinarianNote, setVeterinarianNote] = useState(initial?.veterinarianNote ?? '');
  const [cost, setCost] = useState(initial?.cost ?? '');
  const [note, setNote] = useState(initial?.note ?? '');
  const [rows, setRows] = useState<MedicationRow[]>(
    initial && initial.medications.length > 0
      ? initial.medications.map((med, index) => ({ key: index, ...med }))
      : []
  );
  const [nextKey, setNextKey] = useState(rows.length);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

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

  function handleSubmit() {
    setError(null);

    if (!animalId) {
      setError('Hayvan seçin.');
      return;
    }
    if (!eventTypeId) {
      setError('Olay tipi seçin.');
      return;
    }
    if (!eventDate) {
      setError('Tarih seçin.');
      return;
    }

    const meds: HealthEventMedicationInput[] = [];
    for (const row of rows) {
      if (!row.medicationId) continue; // bos satir - atla
      meds.push({
        medicationId: Number(row.medicationId),
        dosageAmount: row.dosageAmount ? Number(row.dosageAmount) : null,
        dosageUnitId: row.dosageUnitId ? Number(row.dosageUnitId) : null,
      });
    }

    startTransition(async () => {
      const result = eventId
        ? await updateHealthEventAction(
            eventId,
            animalId,
            Number(eventTypeId),
            eventDate,
            diseaseId ? Number(diseaseId) : null,
            meds,
            veterinarianNote.trim() || null,
            cost ? Number(cost) : null,
            note.trim() || null
          )
        : await createHealthEventAction(
            animalId,
            Number(eventTypeId),
            eventDate,
            diseaseId ? Number(diseaseId) : null,
            meds,
            veterinarianNote.trim() || null,
            cost ? Number(cost) : null,
            note.trim() || null
          );
      if (result.error !== undefined) {
        setError(result.error);
        return;
      }
      router.push('/health-events');
    });
  }

  return (
    <div className="max-w-2xl space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Hayvan <span className="text-red-500">*</span>
          </label>
          <select
            value={animalId}
            onChange={(e) => setAnimalId(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="" disabled>
              Seçiniz...
            </option>
            {animals.map((a) => (
              <option key={a.id} value={a.id}>
                {a.label}
              </option>
            ))}
          </select>
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
          <label className="mb-1 block text-sm font-medium text-slate-700">Hastalık/Tanı</label>
          <select
            value={diseaseId}
            onChange={(e) => setDiseaseId(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="">Yok</option>
            {diseases.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">Veteriner Notu</label>
        <textarea
          value={veterinarianNote}
          onChange={(e) => setVeterinarianNote(e.target.value)}
          rows={2}
          className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
        />
      </div>

      <div>
        <div className="mb-2 flex items-center justify-between">
          <label className="block text-sm font-medium text-slate-700">İlaçlar</label>
          <span className="text-xs text-slate-400">Bir muayenede birden fazla ilaç kullanılabilir</span>
        </div>
        <div className="space-y-2">
          {rows.map((row) => (
            <div key={row.key} className="flex flex-wrap items-center gap-2 rounded border border-slate-200 p-2">
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
          className="mt-2 rounded border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          + İlaç Ekle
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Maliyet (TL)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={cost}
            onChange={(e) => setCost(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Not</label>
          <input
            type="text"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
      </div>

      {error && <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      <button
        type="button"
        onClick={handleSubmit}
        disabled={isPending}
        className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {isPending ? 'Kaydediliyor...' : eventId ? 'Değişiklikleri Kaydet' : 'Sağlık Olayını Kaydet'}
      </button>
    </div>
  );
}
