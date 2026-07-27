import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { BulkWeightForm } from '@/components/BulkWeightForm';

export default async function BulkWeightRecordsPage() {
  const statuses = await apiGetSafe<ApiRecord[]>('/animals/statuses', []);
  const activeStatus = statuses.find((s) => s.code === 'AKTIF');
  const animals = activeStatus
    ? await apiGetSafe<ApiRecord[]>(`/animals?status_id=${String(activeStatus.id)}`, [])
    : [];
  const weighingMethods = await apiGetSafe<ApiRecord[]>('/weight-records/weighing-methods', []);

  const animalOptions = animals
    .map((a) => ({
      id: String(a.id),
      tagNumber: String(a.tag_number ?? ''),
      name: a.name ? String(a.name) : undefined,
    }))
    .sort((a, b) => a.tagNumber.localeCompare(b.tagNumber, 'tr-TR'));

  const methodOptions = weighingMethods.map((m) => ({ id: Number(m.id), name: String(m.name) }));

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href="/weight-records" className="text-sm text-slate-500 hover:text-slate-800">
          ← Tartılar
        </Link>
      </div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Toplu Tartı Girişi</h1>
      <p className="mb-4 text-sm text-slate-500">
        Aktif hayvanlar aşağıda listelenir. Tarih ve tartı yöntemini bir kez seçin, sadece tarttığınız hayvanların
        kilosunu girin — boş bırakılan satırlar kaydedilmez.
      </p>
      <BulkWeightForm animals={animalOptions} weighingMethods={methodOptions} />
    </div>
  );
}
