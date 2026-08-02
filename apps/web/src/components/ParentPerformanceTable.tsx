'use client';

import { useMemo, useState } from 'react';
import type { ApiRecord } from '@/lib/api';
import { TableSearch } from '@/components/TableSearch';
import { CsvExportButton } from '@/components/CsvExportButton';
import { PdfExportButton } from '@/components/PdfExportButton';

type SortKey = 'avg_daily_gain_kg' | 'loss_rate';

const SORT_COLUMNS: { key: SortKey; label: string }[] = [
  { key: 'avg_daily_gain_kg', label: 'Ort. Günlük Kilo Artışı' },
  { key: 'loss_rate', label: 'Kayıp Oranı' },
];

function formatGain(value: unknown): string {
  return typeof value === 'number' ? `${value.toFixed(3)} kg/gün` : '—';
}

function formatLossRate(value: unknown): string {
  return typeof value === 'number' ? `%${value}` : '—';
}

function offspringCountLabel(row: ApiRecord): string {
  return `${String(row.offspring_count)} (${String(row.female_count)} Dişi / ${String(row.male_count)} Erkek)`;
}

/** Anne/Baba Bazında Verimlilik Sıralaması raporlarının ortak tablosu -
 * sütun başlığına tıklayınca aktif sıralama kriteri değişir (kilo artışı
 * büyükten küçüğe, kayıp oranı küçükten büyüğe - "en iyi" her zaman
 * üstte). Ebeveyn kimliği (Anne küpe no ya da Baba gösterim önceliği)
 * çağıran taraftan `getParentLabel` ile gelir, bu bileşen ebeveyn
 * türünden bağımsızdır. */
export function ParentPerformanceTable({
  rows,
  getParentLabel,
  parentColumnLabel,
  searchPlaceholder,
  exportFilenamePrefix,
  exportTitle,
}: {
  rows: ApiRecord[];
  getParentLabel: (row: ApiRecord) => string;
  parentColumnLabel: string;
  searchPlaceholder: string;
  exportFilenamePrefix: string;
  exportTitle: string;
}) {
  const [sortKey, setSortKey] = useState<SortKey>('avg_daily_gain_kg');

  const sortedRows = useMemo(() => {
    const withValue = rows.map((row) => ({
      row,
      value: typeof row[sortKey] === 'number' ? (row[sortKey] as number) : null,
    }));
    withValue.sort((a, b) => {
      if (a.value === null && b.value === null) return 0;
      if (a.value === null) return 1;
      if (b.value === null) return -1;
      return sortKey === 'loss_rate' ? a.value - b.value : b.value - a.value;
    });
    return withValue.map((w) => w.row);
  }, [rows, sortKey]);

  if (rows.length === 0) {
    return <p className="text-sm text-slate-500">Henüz yeterli veri yok.</p>;
  }

  const csvHeaders = [parentColumnLabel, 'Yavru Sayısı', 'Ort. Günlük Kilo Artışı', 'Kayıp Oranı'];
  const csvRows = sortedRows.map((row) => [
    getParentLabel(row),
    offspringCountLabel(row),
    formatGain(row.avg_daily_gain_kg),
    formatLossRate(row.loss_rate),
  ]);
  const pdfColumns = [
    { label: parentColumnLabel, width: 'narrow' as const },
    { label: 'Yavru Sayısı', width: 'narrow' as const },
    { label: 'Ort. Günlük Kilo Artışı', width: 'narrow' as const },
    { label: 'Kayıp Oranı', width: 'narrow' as const },
  ];

  return (
    <TableSearch
      placeholder={searchPlaceholder}
      actions={
        <>
          <PdfExportButton title={exportTitle} columns={pdfColumns} rows={csvRows} filename={`${exportFilenamePrefix}.pdf`} />
          <CsvExportButton headers={csvHeaders} rows={csvRows} filename={`${exportFilenamePrefix}.csv`} />
        </>
      }
    >
      {/* Serbest metin (Not benzeri) sütun yok - bkz. HerdAnimalValueTable/
          ReportTable'daki hasWideColumn mantığı - tablo w-full ile
          ZORLANMAZ, doğal genişliğinde kalır. */}
      <div className="overflow-x-auto rounded border border-slate-200">
        <table className="divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr className="divide-x divide-slate-200">
              <th className="whitespace-nowrap px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">
                {parentColumnLabel}
              </th>
              <th className="whitespace-nowrap px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">
                Yavru Sayısı
              </th>
              {SORT_COLUMNS.map((col) => {
                const active = sortKey === col.key;
                return (
                  <th key={col.key} className="whitespace-nowrap px-[0.5ch] py-1.5 text-left">
                    <button
                      type="button"
                      onClick={() => setSortKey(col.key)}
                      className={`inline-flex items-center gap-1 font-medium hover:underline ${
                        active ? 'text-slate-900' : 'text-slate-600'
                      }`}
                    >
                      {col.label}
                      {active && <span aria-hidden="true">▾</span>}
                    </button>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sortedRows.map((row, index) => {
              const label = getParentLabel(row);
              // Sahada takibi kolaylaştırmak için diğer raporlarla aynı
              // zebra gölgelendirme (bkz. ReportTable.tsx).
              const rowBg = index % 2 === 1 ? 'bg-slate-50/70' : '';
              return (
                <tr
                  key={index}
                  data-search={label.toLocaleLowerCase('tr-TR')}
                  className={`divide-x divide-slate-100 ${rowBg}`}
                >
                  <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{label}</td>
                  <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{offspringCountLabel(row)}</td>
                  <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{formatGain(row.avg_daily_gain_kg)}</td>
                  <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{formatLossRate(row.loss_rate)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </TableSearch>
  );
}
