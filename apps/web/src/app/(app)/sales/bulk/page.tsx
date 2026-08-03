import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { BulkSaleForm } from '@/components/BulkSaleForm';

export default async function BulkSalesPage() {
  const statuses = await apiGetSafe<ApiRecord[]>('/animals/statuses', []);
  const activeStatus = statuses.find((s) => s.code === 'AKTIF');
  const animals = activeStatus
    ? await apiGetSafe<ApiRecord[]>(`/animals?status_id=${String(activeStatus.id)}`, [])
    : [];
  const buyers = await apiGetSafe<ApiRecord[]>('/sales/buyers', []);
  const saleTypes = await apiGetSafe<ApiRecord[]>('/sales/types', []);

  const animalOptions = animals
    .map((a) => ({
      id: String(a.id),
      tagNumber: String(a.tag_number ?? ''),
      name: a.name ? String(a.name) : undefined,
    }))
    .sort((a, b) => a.tagNumber.localeCompare(b.tagNumber, 'tr-TR'));

  const buyerOptions = buyers.map((b) => ({ id: Number(b.id), name: String(b.name) }));
  const saleTypeOptions = saleTypes.map((t) => ({ id: Number(t.id), name: String(t.name) }));

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href="/sales" className="text-sm text-slate-500 hover:text-slate-800">
          ← Satışlar
        </Link>
      </div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Toplu Satış Girişi</h1>
      <p className="mb-4 text-sm text-slate-500">
        Aynı gün aynı alıcıya birden fazla hayvan sattığınızda kullanın — tarih/alıcı/satış tipini bir kez seçin,
        sadece sattığınız hayvanlara ağırlık ve tutar girin. Boş bırakılan (tutarsız) satırlar kaydedilmez.
      </p>
      <BulkSaleForm animals={animalOptions} buyers={buyerOptions} saleTypes={saleTypeOptions} />
    </div>
  );
}
