import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { BulkHealthEventForm } from '@/components/BulkHealthEventForm';

function toLookupOptions(records: ApiRecord[]): { id: number; name: string }[] {
  return records.map((r) => ({ id: Number(r.id), name: String(r.name) }));
}

export default async function BulkHealthEventsPage() {
  const statuses = await apiGetSafe<ApiRecord[]>('/animals/statuses', []);
  const activeStatus = statuses.find((s) => s.code === 'AKTIF');
  const animals = activeStatus
    ? await apiGetSafe<ApiRecord[]>(`/animals?status_id=${String(activeStatus.id)}`, [])
    : [];
  const eventTypes = await apiGetSafe<ApiRecord[]>('/health-events/event-types', []);
  const diseases = await apiGetSafe<ApiRecord[]>('/health-events/diseases', []);
  const medications = await apiGetSafe<ApiRecord[]>('/health-events/medications', []);
  const dosageUnits = await apiGetSafe<ApiRecord[]>('/health-events/dosage-units', []);

  const animalOptions = animals
    .map((a) => ({
      id: String(a.id),
      tagNumber: String(a.tag_number ?? ''),
      name: a.name ? String(a.name) : undefined,
    }))
    .sort((a, b) => a.tagNumber.localeCompare(b.tagNumber, 'tr-TR'));

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href="/health-events" className="text-sm text-slate-500 hover:text-slate-800">
          ← Sağlık Olayları
        </Link>
      </div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Toplu Sağlık Olayı Girişi</h1>
      <p className="mb-4 text-sm text-slate-500">
        Aynı gün aynı işlemi (örn. toplu aşılama) gören hayvanlar için kullanın — üstteki bilgiler (tarih, ilaç, doz
        vb.) seçtiğiniz TÜM hayvanlara aynen uygulanır, sadece hangi hayvanların dahil olduğunu işaretlersiniz.
      </p>
      <BulkHealthEventForm
        animals={animalOptions}
        eventTypes={toLookupOptions(eventTypes)}
        diseases={toLookupOptions(diseases)}
        medications={toLookupOptions(medications)}
        dosageUnits={toLookupOptions(dosageUnits)}
      />
    </div>
  );
}
