import type { ApiRecord } from '@/lib/api';
import type { ReportConfig } from '@/lib/reports';

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

  return (
    <div className="overflow-x-auto rounded border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
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
            return (
              <tr key={String(row.animal_id ?? row.pen_id ?? row.breeding_event_id ?? index)} className={highlighted ? 'bg-amber-50' : undefined}>
                {report.columns.map((column) => (
                  <td
                    key={column.key}
                    className={`whitespace-nowrap px-3 py-2 ${highlighted ? 'font-medium text-amber-900' : 'text-slate-700'}`}
                  >
                    {formatCell(row, column)}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
