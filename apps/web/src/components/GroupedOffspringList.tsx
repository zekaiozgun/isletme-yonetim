import type { ApiRecord } from '@/lib/api';
import type { ReportConfig } from '@/lib/reports';
import { TableSearch } from '@/components/TableSearch';

function formatCell(row: ApiRecord, column: ReportConfig['columns'][number]): string {
  const raw = row[column.key];
  if (column.format) return column.format(raw, row);
  if (raw === null || raw === undefined || raw === '') return '—';
  return String(raw);
}

/** Anne/Baba Bazında Yavru Listesi gibi soy kayıtları için - düz bir tablo
 * yerine, her ebeveyni büyük punto bir üst başlık olarak gösterip altına
 * yavrularını sıra numarasıyla listeler (bkz. lib/reports/types.ts
 * ReportConfig.groupBy). Gruplar, satırların sunucudan geldiği sırayla
 * (ilk görülme) listelenir - ekstra bir sıralama yapılmaz. */
export function GroupedOffspringList({
  report,
  rows,
  searchQuery,
}: {
  report: ReportConfig;
  rows: ApiRecord[];
  searchQuery?: string;
}) {
  if (!report.groupBy) return null;
  const { key: groupKey, label: groupLabel } = report.groupBy;

  const groups: { key: string; label: string; children: ApiRecord[] }[] = [];
  const indexByKey = new Map<string, number>();
  for (const row of rows) {
    const key = groupKey(row);
    let index = indexByKey.get(key);
    if (index === undefined) {
      index = groups.length;
      indexByKey.set(key, index);
      groups.push({ key, label: groupLabel(row), children: [] });
    }
    groups[index].children.push(row);
  }

  return (
    <TableSearch serverQuery={searchQuery} placeholder={`${report.title} içinde ara...`}>
      {rows.length === 0 ? (
        <p className="text-sm text-slate-500">
          {searchQuery ? 'Aramanızla eşleşen kayıt yok.' : 'Bu raporda şu anda gösterilecek kayıt yok.'}
        </p>
      ) : (
        <div className="space-y-8">
          {groups.map((group) => (
            <div key={group.key}>
              <h2 className="mb-2 text-lg font-semibold text-slate-900">{group.label}</h2>
              <div className="overflow-x-auto rounded border border-slate-200 print:overflow-visible print:rounded-none print:border-none">
                <table className="w-auto divide-y divide-slate-200 text-sm print:text-[10px]">
                  <thead className="bg-slate-50 print:bg-transparent">
                    <tr className="divide-x divide-slate-200">
                      <th className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">
                        Sıra No
                      </th>
                      {report.columns.map((column) => (
                        <th key={column.key} className="w-[1%] px-[0.5ch] py-1.5 text-left font-medium leading-tight text-slate-600">
                          {column.label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {group.children.map((row, index) => (
                      <tr
                        key={String(row.animal_id ?? index)}
                        className={`divide-x divide-slate-100 ${index % 2 === 1 ? 'bg-slate-50/70' : ''}`}
                      >
                        <td className="w-[1%] whitespace-nowrap px-[0.5ch] py-1.5 text-slate-500">{index + 1}</td>
                        {report.columns.map((column) => (
                          <td key={column.key} className="w-[1%] whitespace-nowrap px-[0.5ch] py-1.5 text-slate-700">
                            {formatCell(row, column)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}
    </TableSearch>
  );
}
