'use client';

import { useMemo, useState } from 'react';
import type { ApiRecord } from '@/lib/api';
import { formatAgeMixed, formatGenderShort, formatSourceCode, formatValuationStatus } from '@/lib/reports';
import { formatCurrencyTRY as formatCurrency, formatUsdValue as formatUsd } from '@/lib/format';
import { TableSearch } from '@/components/TableSearch';
import { CsvExportButton } from '@/components/CsvExportButton';
import { PdfExportButton } from '@/components/PdfExportButton';

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

  const csvHeaders = ['Küpe No', 'D/E', 'Yaş', 'Tutar (TL)', 'Tutar ($)', 'Durum', 'Kaynak'];
  const csvRows = rows.map((row) => [
    String(row.tag_number ?? ''),
    formatGenderShort(row.gender_name),
    formatAgeMixed(row.age_months, row),
    formatCurrency(Number(row.amount_try ?? 0)),
    formatUsd(Number(row.amount_usd ?? 0)),
    formatValuationStatus(row.status_code),
    formatSourceCode(row.source_code),
  ]);
  const pdfColumns = [
    { label: 'Küpe No', width: 'narrow' as const },
    { label: 'D/E', width: 'narrow' as const },
    { label: 'Yaş', width: 'narrow' as const },
    { label: 'Tutar (TL)', width: 'narrow' as const },
    { label: 'Tutar ($)', width: 'narrow' as const },
    { label: 'Durum', width: 'narrow' as const },
    { label: 'Kaynak', width: 'narrow' as const },
  ];

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
        actions={
          <>
            <PdfExportButton
              title="Sürü Hayvan Listesi - Tahmini Piyasa Değeri"
              columns={pdfColumns}
              rows={csvRows}
              filename="herd-animal-market-values.pdf"
            />
            <CsvExportButton headers={csvHeaders} rows={csvRows} filename="herd-animal-market-values.csv" />
          </>
        }
      >
        <div className="overflow-x-auto rounded border border-slate-200">
          {/* Bu tabloda serbest metin (Not benzeri) sütun yok - hepsi kısa
              sabit-format değerler, bu yüzden diğer raporlardaki gibi
              (bkz. ReportTable.tsx hasWideColumn) w-full ile ZORLANMAZ;
              tablo doğal (içeriğe göre) genişliğinde kalır. */}
          <table className="divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr className="divide-x divide-slate-200">
                <th className="w-[1%] px-[0.5ch] py-1.5 text-left">
                  <input
                    type="checkbox"
                    checked={selected.size === rows.length}
                    onChange={toggleAll}
                    aria-label="Tümünü seç"
                  />
                </th>
                <th className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">Küpe No</th>
                <th className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">D/E</th>
                <th className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">Yaş</th>
                <th className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">Tutar (TL)</th>
                <th className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">Tutar ($)</th>
                <th className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">Durum</th>
                <th className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">Kaynak</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((row, index) => {
                const id = String(row.animal_id);
                const checked = selected.has(id);
                const searchText = [row.tag_number, row.gender_name]
                  .map((v) => String(v ?? ''))
                  .join(' ')
                  .toLocaleLowerCase('tr-TR');
                // Sahada takibi kolaylaştırmak için diğer raporlarla aynı
                // zebra gölgelendirme (bkz. ReportTable.tsx) - seçili satır
                // zebra deseninin önüne geçer.
                const rowBg = checked ? 'bg-blue-50' : index % 2 === 1 ? 'bg-slate-50/70' : '';
                return (
                  <tr key={id} data-search={searchText} className={`divide-x divide-slate-100 ${rowBg}`}>
                    <td className="whitespace-nowrap px-[0.5ch] py-1.5">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggle(id)}
                        aria-label={`${String(row.tag_number)} seç`}
                      />
                    </td>
                    <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{String(row.tag_number ?? '—')}</td>
                    <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{formatGenderShort(row.gender_name)}</td>
                    <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{formatAgeMixed(row.age_months, row)}</td>
                    <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">
                      {formatCurrency(Number(row.amount_try ?? 0))}
                    </td>
                    <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">
                      {formatUsd(Number(row.amount_usd ?? 0))}
                    </td>
                    <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{formatValuationStatus(row.status_code)}</td>
                    <td className="whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">{formatSourceCode(row.source_code)}</td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr className="divide-x divide-slate-100 border-t border-slate-300 bg-slate-50 font-semibold text-slate-900">
                <td className="px-[0.5ch] py-1.5" />
                <td className="whitespace-nowrap px-[0.5ch] py-1.5" colSpan={2}>
                  TOPLAM ({rows.length} hayvan)
                </td>
                <td className="px-[0.5ch] py-1.5" />
                <td className="whitespace-nowrap px-[0.5ch] py-1.5">{formatCurrency(grandTotal.try_)}</td>
                <td className="whitespace-nowrap px-[0.5ch] py-1.5">{formatUsd(grandTotal.usd)}</td>
                <td className="px-[0.5ch] py-1.5" />
                <td className="px-[0.5ch] py-1.5" />
              </tr>
            </tfoot>
          </table>
        </div>
      </TableSearch>
    </div>
  );
}
