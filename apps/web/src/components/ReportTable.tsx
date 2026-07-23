import type { ApiRecord } from '@/lib/api';
import type { ReportConfig } from '@/lib/reports';
import { TableSearch } from '@/components/TableSearch';
import { CsvExportButton } from '@/components/CsvExportButton';

function formatCell(row: ApiRecord, column: ReportConfig['columns'][number]): string {
  const raw = row[column.key];
  if (column.format) return column.format(raw, row);
  if (raw === null || raw === undefined || raw === '') return '—';
  return String(raw);
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

  return (
    <TableSearch
      placeholder={`${report.title} içinde ara...`}
      actions={<CsvExportButton headers={csvHeaders} rows={csvRows} filename={`${report.slug}.csv`} />}
    >
      <div className="overflow-x-auto rounded border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-slate-600">#</th>
              {report.columns.map((column) => (
                <th key={column.key} className="px-3 py-2 text-left font-medium text-slate-600">
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
              return (
                <tr
                  key={String(row.animal_id ?? row.pen_id ?? row.breeding_event_id ?? index)}
                  data-search={searchText}
                  className={highlighted ? 'bg-amber-50' : undefined}
                >
                  <td className={`whitespace-nowrap px-3 py-2 ${highlighted ? 'font-medium text-amber-900' : 'text-slate-500'}`}>
                    {index + 1}
                  </td>
                  {report.columns.map((column, columnIndex) => (
                    <td
                      key={column.key}
                      className={`whitespace-nowrap px-3 py-2 ${highlighted ? 'font-medium text-amber-900' : 'text-slate-700'}`}
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
  );
}
