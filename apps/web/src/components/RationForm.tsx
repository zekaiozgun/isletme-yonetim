'use client';

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { createPenRationAction, type RationItemInput } from '@/lib/actions';

interface PenOption {
  id: number;
  label: string;
}

interface FeedItemOption {
  id: number;
  name: string;
}

interface UnitOption {
  id: number;
  name: string;
}

interface ItemRow {
  key: number;
  feedItemId: string;
  dailyQuantityPerAnimal: string;
  unitId: string;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function emptyRow(key: number, defaultUnitId: string): ItemRow {
  return { key, feedItemId: '', dailyQuantityPerAnimal: '', unitId: defaultUnitId };
}

export function RationForm({ pens, feedItems, units }: { pens: PenOption[]; feedItems: FeedItemOption[]; units: UnitOption[] }) {
  const router = useRouter();
  const defaultUnitId = units[0] ? String(units[0].id) : '';
  const [penId, setPenId] = useState('');
  const [startDate, setStartDate] = useState(todayIso());
  const [note, setNote] = useState('');
  const [rows, setRows] = useState<ItemRow[]>([emptyRow(0, defaultUnitId)]);
  const [nextKey, setNextKey] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function updateRow(key: number, patch: Partial<ItemRow>) {
    setRows((prev) => prev.map((row) => (row.key === key ? { ...row, ...patch } : row)));
  }

  function addRow() {
    setRows((prev) => [...prev, emptyRow(nextKey, defaultUnitId)]);
    setNextKey((k) => k + 1);
  }

  function removeRow(key: number) {
    setRows((prev) => (prev.length > 1 ? prev.filter((row) => row.key !== key) : prev));
  }

  function handleSubmit() {
    setError(null);

    if (!penId) {
      setError('Padok seçin.');
      return;
    }
    if (!startDate) {
      setError('Başlangıç tarihi seçin.');
      return;
    }

    const items: RationItemInput[] = [];
    for (const row of rows) {
      if (!row.feedItemId && !row.dailyQuantityPerAnimal) continue; // bos satir - atla
      if (!row.feedItemId || !row.dailyQuantityPerAnimal || !row.unitId) {
        setError('Her rasyon kalemi için yem ürünü, miktar ve birim seçilmeli.');
        return;
      }
      const quantity = Number(row.dailyQuantityPerAnimal);
      if (Number.isNaN(quantity) || quantity <= 0) {
        setError('Miktarlar geçerli bir pozitif sayı olmalı.');
        return;
      }
      items.push({ feedItemId: Number(row.feedItemId), dailyQuantityPerAnimal: quantity, unitId: Number(row.unitId) });
    }

    if (items.length === 0) {
      setError('En az bir rasyon kalemi (yem ürünü + miktar) girin.');
      return;
    }

    startTransition(async () => {
      const result = await createPenRationAction(Number(penId), startDate, note, items);
      if (result.error !== undefined) {
        setError(result.error);
        return;
      }
      router.push('/pen-rations');
    });
  }

  return (
    <div className="max-w-2xl space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Padok <span className="text-red-500">*</span>
          </label>
          <select
            value={penId}
            onChange={(e) => setPenId(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="" disabled>
              Seçiniz...
            </option>
            {pens.map((pen) => (
              <option key={pen.id} value={pen.id}>
                {pen.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Başlangıç Tarihi <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          />
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">Not</label>
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          rows={2}
          className="w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
        />
      </div>

      <div>
        <div className="mb-2 flex items-center justify-between">
          <label className="block text-sm font-medium text-slate-700">
            Rasyon Kalemleri <span className="text-red-500">*</span>
          </label>
          <span className="text-xs text-slate-400">Miktar: hayvan başına, günlük</span>
        </div>
        <div className="space-y-2">
          {rows.map((row) => (
            <div key={row.key} className="flex items-center gap-2 rounded border border-slate-200 p-2">
              <select
                value={row.feedItemId}
                onChange={(e) => updateRow(row.key, { feedItemId: e.target.value })}
                className="flex-1 rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
              >
                <option value="">Yem ürünü seçin...</option>
                {feedItems.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
              <input
                type="number"
                step="0.001"
                min="0"
                placeholder="Miktar"
                value={row.dailyQuantityPerAnimal}
                onChange={(e) => updateRow(row.key, { dailyQuantityPerAnimal: e.target.value })}
                className="w-28 rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
              />
              <select
                value={row.unitId}
                onChange={(e) => updateRow(row.key, { unitId: e.target.value })}
                className="w-24 rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
              >
                {units.map((unit) => (
                  <option key={unit.id} value={unit.id}>
                    {unit.name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => removeRow(row.key)}
                disabled={rows.length === 1}
                className="rounded px-2 py-1.5 text-sm text-slate-400 hover:bg-slate-100 hover:text-red-600 disabled:opacity-30"
                aria-label="Kalemi kaldır"
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
          + Kalem Ekle
        </button>
      </div>

      {error && <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      <button
        type="button"
        onClick={handleSubmit}
        disabled={isPending}
        className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {isPending ? 'Kaydediliyor...' : 'Rasyonu Kaydet'}
      </button>
    </div>
  );
}
