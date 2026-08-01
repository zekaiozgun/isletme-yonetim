import type { ApiRecord } from '@/lib/api';

export function ParentPerformanceSection({ motherRows, sireRows }: { motherRows: ApiRecord[]; sireRows: ApiRecord[] }) {
  return (
    <div>
      <p>DEBUG2 motherRows: {motherRows.length}, sireRows: {sireRows.length}</p>
    </div>
  );
}
