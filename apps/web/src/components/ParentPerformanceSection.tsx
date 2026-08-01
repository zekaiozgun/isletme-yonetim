'use client';

import type { ApiRecord } from '@/lib/api';
import { formatSireIdentity } from '@/lib/reports';
import { ParentPerformanceTable } from '@/components/ParentPerformanceTable';

function motherLabel(row: ApiRecord): string {
  return String(row.mother_tag_number ?? '—');
}

function sireLabel(row: ApiRecord): string {
  return formatSireIdentity(row.sire_id, row);
}

/** Anne ve Baba Bazında Verimlilik Sıralaması - tek rapor girişinden,
 * iki ayrı tabloya (bölüme) ayrılır. Her iki tablo da aynı bileşeni
 * (ParentPerformanceTable) kullanır, sadece ebeveyn kimliği farklı
 * gösterilir (Anne: küpe no, Baba: formatSireIdentity önceliği). */
export function ParentPerformanceSection({ motherRows, sireRows }: { motherRows: ApiRecord[]; sireRows: ApiRecord[] }) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Anne Bazında</h2>
        <ParentPerformanceTable
          rows={motherRows}
          getParentLabel={motherLabel}
          parentColumnLabel="Anne Küpe No"
          searchPlaceholder="Anne Bazında ara (küpe no)..."
          exportFilenamePrefix="anne-bazinda-verimlilik"
          exportTitle="Anne Bazında Verimlilik Sıralaması"
        />
      </div>
      <div>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Baba Bazında</h2>
        <ParentPerformanceTable
          rows={sireRows}
          getParentLabel={sireLabel}
          parentColumnLabel="Baba"
          searchPlaceholder="Baba Bazında ara (ad/kayıt no)..."
          exportFilenamePrefix="baba-bazinda-verimlilik"
          exportTitle="Baba Bazında Verimlilik Sıralaması"
        />
      </div>
    </div>
  );
}
