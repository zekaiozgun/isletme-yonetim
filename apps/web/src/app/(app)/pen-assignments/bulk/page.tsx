import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { getResource, getRelatedLookups } from '@/lib/resources';
import { BulkPenAssignmentForm } from '@/components/BulkPenAssignmentForm';
import { RelatedLookupsBar } from '@/components/RelatedLookupsBar';

export default async function BulkPenAssignmentsPage() {
  const statuses = await apiGetSafe<ApiRecord[]>('/animals/statuses', []);
  const activeStatus = statuses.find((s) => s.code === 'AKTIF');
  const animals = activeStatus
    ? await apiGetSafe<ApiRecord[]>(`/animals?status_id=${String(activeStatus.id)}`, [])
    : [];
  const pens = await apiGetSafe<ApiRecord[]>('/pens', []);
  const reasons = await apiGetSafe<ApiRecord[]>('/pens/pen-assignment-reasons', []);

  const animalOptions = animals
    .map((a) => ({
      id: String(a.id),
      tagNumber: String(a.tag_number ?? ''),
      name: a.name ? String(a.name) : undefined,
    }))
    .sort((a, b) => a.tagNumber.localeCompare(b.tagNumber, 'tr-TR'));

  const penOptions = pens.map((p) => ({ id: Number(p.id), name: `${String(p.code)} - ${String(p.name)}` }));
  const reasonOptions = reasons.map((r) => ({ id: Number(r.id), name: String(r.name) }));

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href="/pen-assignments" className="text-sm text-slate-500 hover:text-slate-800">
          ← Padok Atamaları
        </Link>
      </div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Toplu Padok Ataması</h1>
      <p className="mb-4 text-sm text-slate-500">
        Bir grup hayvanı (örn. sütten kesim grubu) aynı anda yeni padoğa taşımak için kullanın — hedef padok/tarih/
        neden seçtiğiniz TÜM hayvanlara aynen uygulanır, sadece hangi hayvanların dahil olduğunu işaretlersiniz.
      </p>
      <RelatedLookupsBar items={getRelatedLookups(getResource('pen-assignments')!)} />
      <BulkPenAssignmentForm animals={animalOptions} pens={penOptions} reasons={reasonOptions} />
    </div>
  );
}
