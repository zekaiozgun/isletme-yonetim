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

// A4 baskıya uygun mizanpaj: dar sütunlar (tarih/yaş/sayı) sıkışıklık
// hissi vermeyecek 1 karakterlik dolguyla dar tutulur; geniş sütunlar
// (serbest metin) tek satırda kalıp taşarsa "…" ile kesilir (title
// attribute'u üzerine gelince tam metni gösterir - bkz. ReportTable altı).
function widthClass(width: ReportConfig['columns'][number]['width']): string {
  if (width === 'narrow') return 'whitespace-nowrap px-[1ch] py-2';
  if (width === 'wide') return 'max-w-sm truncate px-3 py-2';
  return 'whitespace-nowrap px-3 py-2';
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

export function ReportTable({ report, rows }: { report: ReportConfig; rows: ApiRecord[] }) {
  if (rows.length === 0) {
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
        <div className="overflow-x-auto rounded border border-slate-200 print:overflow-visible print:rounded-none print:border-none">
          <table className="min-w-full divide-y divide-slate-200 text-sm print:w-full print:text-[10px]">
            <thead className="bg-slate-50 print:bg-transparent">
              <tr>
                <th className="whitespace-nowrap px-[1ch] py-2 text-left font-medium text-slate-600">#</th>
                {report.columns.map((column) => (
                  <th
                    key={column.key}
                    className={`text-left font-medium text-slate-600 ${widthClass(column.width)}`}
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
                  <tr key={String(row.animal_id ?? row.pen_id ?? row.breeding_event_id ?? index)} data-search={searchText} className={rowBg}>
                    <td
                      className={`whitespace-nowrap px-[1ch] py-2 ${highlighted ? 'font-medium text-amber-900' : 'text-slate-500'}`}
                    >
                      {index + 1}
                    </td>
                    {report.columns.map((column, columnIndex) => (
                      <td
                        key={column.key}
                        title={column.width === 'wide' ? cellValues[columnIndex] : undefined}
                        className={`${widthClass(column.width)} ${highlighted ? 'font-medium text-amber-900' : 'text-slate-700'}`}
                      >
                        {cellValues[columnIndex]}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </TableSearch>
    </>
  );
}
