'use client';

import { useMemo, useState } from 'react';
import type { ApiRecord } from '@/lib/api';
import { TableSearch } from '@/components/TableSearch';
import { CsvExportButton } from '@/components/CsvExportButton';
import { PdfExportButton } from '@/components/PdfExportButton';

type SortKey = 'avg_daily_gain_kg' | 'died_count' | 'loss_rate';

const SORT_LABELS: Record<SortKey, string> = {
  avg_daily_gain_kg: 'Ort. Günlük Kilo Artışı',
  died_count: 'Ölen',
  loss_rate: 'Kayıp Oranı',
};

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
 * büyükten küçüğe, kayıp/ölen sayısı küçükten büyüğe - "en iyi" her zaman
 * üstte). Ebeveyn kimliği (Anne küpe no ya da Baba gösterim önceliği)
 * çağıran taraftan `getParentLabel` ile gelir, bu bileşen ebeveyn
 * türünden bağımsızdır. Sütun sırası BİLEREK bu şekilde (Yavru Sayısı,
 * Kilo Artışı, sonra yan yana Hayatta/Ölen, sonra Kayıp Oranı) - bkz.
 * kullanıcı geri bildirimi. "Ort. Günlük Kilo Artışı" başlığı kelime
 * kelime alt alta yazılır (br ile) - sütunun kendisi diğerlerinden çok
 * daha geniş bir başlık yüzünden gereksiz genişlemesin diye. */
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
      // Kilo artisinda buyuk-kucuk (en iyi ustte), kayip/olen sayisinda
      // kucuk-buyuk (en AZ kayip ustte) siralanir - ikisinde de "en iyi"
      // her zaman en ustte.
      return sortKey === 'loss_rate' || sortKey === 'died_count' ? a.value - b.value : b.value - a.value;
    });
    return withValue.map((w) => w.row);
  }, [rows, sortKey]);

  if (rows.length === 0) {
    return <p className="text-sm text-slate-500">Henüz yeterli veri yok.</p>;
  }

  function sortButton(key: SortKey, content: React.ReactNode) {
    const active = sortKey === key;
    return (
      <button
        type="button"
        onClick={() => setSortKey(key)}
        className={`inline-flex items-center gap-1 font-medium hover:underline ${
          active ? 'text-slate-900' : 'text-slate-600'
        }`}
      >
        {content}
        {active && <span aria-hidden="true">▾</span>}
      </button>
    );
  }

  const csvHeaders = [
    parentColumnLabel,
    'Yavru Sayısı',
    SORT_LABELS.avg_daily_gain_kg,
    'Hayatta',
    SORT_LABELS.died_count,
    SORT_LABELS.loss_rate,
  ];
  const csvRows = sortedRows.map((row) => [
    getParentLabel(row),
    offspringCountLabel(row),
    formatGain(row.avg_daily_gain_kg),
    String(row.alive_count),
    String(row.died_count),
    formatLossRate(row.loss_rate),
  ]);
  const pdfColumns = [
    { label: parentColumnLabel, width: 'narrow' as const },
    { label: 'Yavru Sayısı', width: 'narrow' as const },
    { label: SORT_LABELS.avg_daily_gain_kg, width: 'narrow' as const },
    { label: 'Hayatta', width: 'narrow' as const },
    { label: SORT_LABELS.died_count, width: 'narrow' as const },
    { label: SORT_LABELS.loss_rate, width: 'narrow' as const },
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
              <th className="whitespace-nowrap px-[0.5ch] py-1.5 text-left leading-tight">
                {sortButton(
                  'avg_daily_gain_kg',
                  <span>
                    Ort.
                    <br />
                    Günlük
                    <br />
                    Kilo
                    <br />
                    Artışı
                  </span>
                )}
              </th>
              <th className="whitespace-nowrap px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">
                Hayatta
              </th>
              <th className="whitespace-nowrap px-[0.5ch] py-1.5 text-left">{sortButton('died_count', SORT_LABELS.died_count)}</th>
              <th className="whitespace-nowrap px-[0.5ch] py-1.5 text-left">{sortButton('loss_rate', SORT_LABELS.loss_rate)}</th>
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
                  <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{String(row.alive_count)}</td>
                  <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{String(row.died_count)}</td>
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
