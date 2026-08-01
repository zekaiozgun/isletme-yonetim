import type { ApiRecord } from '@/lib/api';
import type { ReportConfig } from '@/lib/reports';
import { TableSearch } from '@/components/TableSearch';
import { CsvExportButton } from '@/components/CsvExportButton';
import { PdfExportButton } from '@/components/PdfExportButton';

function formatCell(row: ApiRecord, column: ReportConfig['columns'][number]): string {
  const raw = row[column.key];
  if (column.format) return column.format(raw, row);
  if (raw === null || raw === undefined || raw === '') return '—';
  return String(raw);
}

// A4 baskıya uygun mizanpaj: tablo container'in tam genisligini kaplar
// (w-full), ama dar/varsayilan sutunlar "w-[1%]" hilesiyle sadece
// icerigi kadar yer kaplar (table-layout:auto'da width:1% pratikte
// "mumkun oldugunca kucul" anlamina gelir) - boyle bosta kalan TUM alan
// otomatik olarak "wide" (serbest metin, orn. Not) sutununa gider,
// hicbir JS/olcum gerekmeden. Wide sutun artik kesilmiyor, tasarsa
// birden fazla satira SARILIYOR (tam metin her zaman gorunur).
function widthClass(width: ReportConfig['columns'][number]['width']): string {
  if (width === 'narrow') return 'whitespace-nowrap px-[0.5ch] py-1.5 w-[1%]';
  if (width === 'wide') return 'whitespace-normal break-words px-[0.5ch] py-1.5';
  return 'whitespace-nowrap px-[0.5ch] py-1.5 w-[1%]';
}

// Başlıklar - veri hücrelerinin aksine - tek satıra sığmıyorsa iki satıra
// SARILIR (nowrap yok) - böylece uzun bir etiket (örn. "Tohumlama Tarihi")
// altındaki kısa değerleri (örn. "29/04/2026") gereksiz yere
// genişletmez, sütun asıl içeriğe göre dar kalabilir.
function headerClass(width: ReportConfig['columns'][number]['width']): string {
  const widthHint = width === 'wide' ? '' : ' w-[1%]';
  return `px-[0.5ch] py-1.5 leading-tight${widthHint}`;
}

// report.groupSummaryKey belirtilen sutunun degerine gore kayit sayisini
// gruplar (orn. statu bazinda kac buzagi) - arama kutusundan bagimsiz,
// her zaman TAM veri setinin toplamini gosterir.
function GroupSummary({ rows, groupKey }: { rows: ApiRecord[]; groupKey: string }) {
  const counts = new Map<string, number>();
  for (const row of rows) {
    const raw = row[groupKey];
    const value = raw === null || raw === undefined || raw === '' ? '—' : String(raw);
    counts.set(value, (counts.get(value) ?? 0) + 1);
  }
  const entries = Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
  return (
    <div className="mb-3 flex flex-wrap items-center gap-2 text-sm print:mb-2">
      <span className="rounded-full bg-slate-900 px-3 py-1 font-medium text-white">Toplam: {rows.length}</span>
      {entries.map(([value, count]) => (
        <span key={value} className="rounded-full bg-slate-100 px-3 py-1 text-slate-700">
          {value}: {count}
        </span>
      ))}
    </div>
  );
}

export function ReportTable({
  report,
  rows,
  serverQuery,
}: {
  report: ReportConfig;
  rows: ApiRecord[];
  /** report.serverSearch true ise mevcut arama sorgusu (bkz. TableSearch) -
   * verilirse, 0 satır dönse bile arama kutusu (sorguyu değiştirebilsin
   * diye) HER ZAMAN gösterilir; verilmezse (client-side arama) 0 satırda
   * eskisi gibi tek bir "kayıt yok" mesajıyla erken çıkılır. */
  serverQuery?: string;
}) {
  if (rows.length === 0 && serverQuery === undefined) {
    return <p className="text-sm text-slate-500">Bu raporda şu anda gösterilecek kayıt yok.</p>;
  }

  const csvHeaders = ['#', ...report.columns.map((c) => c.label)];
  const csvRows = rows.map((row, index) => [
    String(index + 1),
    ...report.columns.map((column) => formatCell(row, column)),
  ]);
  const pdfColumns = [{ label: '#', width: 'narrow' as const }, ...report.columns.map((c) => ({ label: c.label, width: c.width }))];
  const highlightedRows = rows
    .map((row, index) => (report.rowHighlight?.(row) ? index : -1))
    .filter((index) => index !== -1);

  return (
    <>
      {report.groupSummaryKey && <GroupSummary rows={rows} groupKey={report.groupSummaryKey} />}
      <TableSearch
        placeholder={`${report.title} içinde ara...`}
        serverQuery={serverQuery}
        actions={
          <>
            <PdfExportButton
              title={report.title}
              description={report.description}
              columns={pdfColumns}
              rows={csvRows}
              highlightedRows={highlightedRows}
              filename={`${report.slug}.pdf`}
            />
            <CsvExportButton headers={csvHeaders} rows={csvRows} filename={`${report.slug}.csv`} />
          </>
        }
      >
        {rows.length === 0 ? (
          <p className="text-sm text-slate-500">Aramanızla eşleşen kayıt yok.</p>
        ) : (
          <div className="overflow-x-auto rounded border border-slate-200 print:overflow-visible print:rounded-none print:border-none">
            <table className="w-full divide-y divide-slate-200 text-sm print:text-[10px]">
              <thead className="bg-slate-50 print:bg-transparent">
                <tr className="divide-x divide-slate-200">
                  <th className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">#</th>
                  {report.columns.map((column) => (
                    <th
                      key={column.key}
                      className={`text-left font-medium text-slate-600 ${headerClass(column.width)}`}
                    >
                      {column.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rows.map((row, index) => {
                  const highlighted = report.rowHighlight?.(row) ?? false;
                  const cellValues = report.columns.map((column) => formatCell(row, column));
                  const searchText = cellValues.join(' ').toLocaleLowerCase('tr-TR');
                  const rowBg = highlighted ? 'bg-amber-50' : index % 2 === 1 ? 'bg-slate-50/70' : undefined;
                  return (
                    <tr
                      key={String(row.animal_id ?? row.pen_id ?? row.breeding_event_id ?? index)}
                      data-search={searchText}
                      className={`divide-x divide-slate-100 ${rowBg ?? ''}`}
                    >
                      <td
                        className={`w-[1%] whitespace-nowrap px-[0.5ch] py-1.5 ${highlighted ? 'font-medium text-amber-900' : 'text-slate-500'}`}
                      >
                        {index + 1}
                      </td>
                      {report.columns.map((column, columnIndex) => {
                        const cellExtra = column.cellClassName?.(row);
                        const textClass = cellExtra ?? (highlighted ? 'font-medium text-amber-900' : 'text-slate-700');
                        return (
                          <td key={column.key} className={`${widthClass(column.width)} ${textClass}`}>
                            {cellValues[columnIndex]}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </TableSearch>
    </>
  );
}
