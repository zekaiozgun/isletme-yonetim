'use client';

import { useMemo, useState } from 'react';
import type { ApiRecord } from '@/lib/api';
import { formatMonths, formatSourceCode } from '@/lib/reports';
import { TableSearch } from '@/components/TableSearch';
import { CsvExportButton } from '@/components/CsvExportButton';

function formatCurrency(value: number): string {
  return `${value.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₺`;
}

function formatUsd(value: number): string {
  return `$${value.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function HerdAnimalValueTable({ rows }: { rows: ApiRecord[] }) {
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const totals = useMemo(() => {
    let try_ = 0;
    let usd = 0;
    for (const row of rows) {
      const id = String(row.animal_id);
      if (!selected.has(id)) continue;
      try_ += Number(row.amount_try ?? 0);
      usd += Number(row.amount_usd ?? 0);
    }
    return { try_, usd };
  }, [rows, selected]);

  // Tum sürünün toplamı (seçime bakmaksızın) - aynı as_of_date için Sürü
  // Tahmini Piyasa Değeri raporundaki nokta ile BİREBİR AYNI olması
  // gerekir, çünkü ikisi de aynı _estimated_market_value_usd_try
  // hesaplamasının üzerine kuruludur.
  const grandTotal = useMemo(() => {
    let try_ = 0;
    let usd = 0;
    for (const row of rows) {
      try_ += Number(row.amount_try ?? 0);
      usd += Number(row.amount_usd ?? 0);
    }
    return { try_, usd };
  }, [rows]);

  if (rows.length === 0) {
    return <p className="text-sm text-slate-500">Bu tarihte yaşayan hayvan bulunamadı.</p>;
  }

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleAll() {
    setSelected((prev) => (prev.size === rows.length ? new Set() : new Set(rows.map((r) => String(r.animal_id)))));
  }

  const csvHeaders = ['Küpe No', 'İsim', 'Cinsiyet', 'Yaş', 'Tutar (TL)', 'Tutar ($)', 'Kaynak'];
  const csvRows = rows.map((row) => [
    String(row.tag_number ?? ''),
    String(row.name ?? ''),
    String(row.gender_name ?? ''),
    formatMonths(row.age_months),
    formatCurrency(Number(row.amount_try ?? 0)),
    formatUsd(Number(row.amount_usd ?? 0)),
    formatSourceCode(row.source_code),
  ]);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3 rounded border border-slate-300 bg-slate-100 px-3 py-2 text-sm">
        <span className="font-medium text-slate-700">Sürü Toplamı ({rows.length} hayvan):</span>
        <span className="font-semibold text-slate-900">{formatCurrency(grandTotal.try_)}</span>
        <span className="font-semibold text-slate-900">{formatUsd(grandTotal.usd)}</span>
      </div>
      {selected.size > 0 && (
        <div className="flex flex-wrap items-center gap-3 rounded border border-slate-300 bg-slate-50 px-3 py-2 text-sm">
          <span className="font-medium text-slate-700">Seçilenler ({selected.size} hayvan):</span>
          <span className="font-semibold text-slate-900">{formatCurrency(totals.try_)}</span>
          <span className="font-semibold text-slate-900">{formatUsd(totals.usd)}</span>
        </div>
      )}
      <TableSearch
        placeholder="Sürü Hayvan Listesi içinde ara..."
        actions={<CsvExportButton headers={csvHeaders} rows={csvRows} filename="herd-animal-market-values.csv" />}
      >
        <div className="overflow-x-auto rounded border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-3 py-2 text-left">
                  <input
                    type="checkbox"
                    checked={selected.size === rows.length}
                    onChange={toggleAll}
                    aria-label="Tümünü seç"
                  />
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Küpe No</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">İsim</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Cinsiyet</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Yaş</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Tutar (TL)</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Tutar ($)</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Kaynak</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((row) => {
                const id = String(row.animal_id);
                const checked = selected.has(id);
                const searchText = [row.tag_number, row.name, row.gender_name]
                  .map((v) => String(v ?? ''))
                  .join(' ')
                  .toLocaleLowerCase('tr-TR');
                return (
                  <tr key={id} data-search={searchText} className={checked ? 'bg-blue-50' : undefined}>
                    <td className="whitespace-nowrap px-3 py-2">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggle(id)}
                        aria-label={`${String(row.tag_number)} seç`}
                      />
                    </td>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">{String(row.tag_number ?? '—')}</td>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">{String(row.name ?? '—')}</td>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">{String(row.gender_name ?? '—')}</td>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">{formatMonths(row.age_months)}</td>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">
                      {formatCurrency(Number(row.amount_try ?? 0))}
                    </td>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">{formatUsd(Number(row.amount_usd ?? 0))}</td>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">{formatSourceCode(row.source_code)}</td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr className="border-t border-slate-300 bg-slate-50 font-semibold text-slate-900">
                <td className="px-3 py-2" />
                <td className="px-3 py-2" colSpan={3}>
                  TOPLAM ({rows.length} hayvan)
                </td>
                <td className="px-3 py-2" />
                <td className="whitespace-nowrap px-3 py-2">{formatCurrency(grandTotal.try_)}</td>
                <td className="whitespace-nowrap px-3 py-2">{formatUsd(grandTotal.usd)}</td>
                <td className="px-3 py-2" />
              </tr>
            </tfoot>
          </table>
        </div>
      </TableSearch>
    </div>
  );
}
