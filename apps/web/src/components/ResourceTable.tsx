import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import type { ColumnConfig, ResourceConfig } from '@/lib/resources';
import { formatDateDMY } from '@/lib/format';
import { TableSearch } from '@/components/TableSearch';
import { CsvExportButton } from '@/components/CsvExportButton';

async function buildLookupMaps(columns: ColumnConfig[]): Promise<Map<string, Map<string, string>>> {
  const maps = new Map<string, Map<string, string>>();
  const columnsWithLookup = columns.filter((c) => c.lookup);

  await Promise.all(
    columnsWithLookup.map(async (column) => {
      const source = column.lookup!;
      if (maps.has(source.endpoint)) return;
      const items = await apiGetSafe<ApiRecord[]>(source.endpoint, []);
      const map = new Map<string, string>();
      for (const item of items) {
        const value = source.value ? source.value(item) : String(item.id);
        map.set(value, source.label(item));
      }
      maps.set(source.endpoint, map);
    })
  );

  return maps;
}

function formatCell(row: ApiRecord, column: ColumnConfig, lookupMaps: Map<string, Map<string, string>>): string {
  const raw = row[column.key];

  if (column.format) return column.format(raw, row);

  if (raw === null || raw === undefined || raw === '') return '—';

  if (column.boolean) return raw ? 'Evet' : 'Hayır';

  if (column.date) return formatDateDMY(raw);

  if (column.lookup) {
    const map = lookupMaps.get(column.lookup.endpoint);
    const resolved = map?.get(String(raw));
    return resolved ?? `#${String(raw)}`;
  }

  return String(raw);
}

export async function ResourceTable({ resource, rows }: { resource: ResourceConfig; rows: ApiRecord[] }) {
  const lookupMaps = await buildLookupMaps(resource.columns);

  if (rows.length === 0) {
    return <p className="text-sm text-slate-500">Henüz kayıt yok.</p>;
  }

  const csvHeaders = ['#', ...resource.columns.map((c) => c.label)];
  const tableRows = rows.map((row, index) => ({
    row,
    index,
    cellValues: resource.columns.map((column) => formatCell(row, column, lookupMaps)),
  }));
  const csvRows = tableRows.map(({ index, cellValues }) => [String(index + 1), ...cellValues]);

  return (
    <TableSearch
      placeholder={`${resource.title} içinde ara...`}
      actions={<CsvExportButton headers={csvHeaders} rows={csvRows} filename={`${resource.slug}.csv`} />}
    >
      <div className="overflow-x-auto rounded border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-slate-600">#</th>
              {resource.columns.map((column) => (
                <th key={column.key} className="px-3 py-2 text-left font-medium text-slate-600">
                  {column.label}
                </th>
              ))}
              <th className="px-3 py-2 text-left font-medium text-slate-600">İşlemler</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {tableRows.map(({ row, index, cellValues }) => {
              const searchText = cellValues.join(' ').toLocaleLowerCase('tr-TR');
              return (
                <tr key={String(row.id)} data-search={searchText}>
                  <td className="whitespace-nowrap px-3 py-2 text-slate-500">{index + 1}</td>
                  {resource.columns.map((column, columnIndex) => (
                    <td key={column.key} className="whitespace-nowrap px-3 py-2 text-slate-700">
                      {cellValues[columnIndex]}
                    </td>
                  ))}
                  <td className="whitespace-nowrap px-3 py-2">
                    <Link href={`/${resource.slug}/${row.id}`} className="text-sm text-slate-600 hover:text-slate-900 hover:underline">
                      Düzenle
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </TableSearch>
  );
}
