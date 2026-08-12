import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { getResource, getRelatedLookups } from '@/lib/resources';
import { BulkPregnancyCheckForm } from '@/components/BulkPregnancyCheckForm';
import { RelatedLookupsBar } from '@/components/RelatedLookupsBar';

export default async function BulkPregnancyChecksPage() {
  const pendingEvents = await apiGetSafe<ApiRecord[]>('/breeding-events?pending_check=true', []);
  const methods = await apiGetSafe<ApiRecord[]>('/breeding-events/pregnancy-check-methods', []);
  const results = await apiGetSafe<ApiRecord[]>('/breeding-events/pregnancy-results', []);

  const pendingOptions = pendingEvents
    .map((e) => ({
      id: Number(e.id),
      tagNumber: String(e.dam_tag_number ?? '?'),
      serviceDate: String(e.service_date ?? ''),
    }))
    .sort((a, b) => a.tagNumber.localeCompare(b.tagNumber, 'tr-TR'));

  const methodOptions = methods.map((m) => ({ id: Number(m.id), name: String(m.name) }));
  const resultOptions = results.map((r) => ({ id: Number(r.id), name: String(r.name) }));

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href="/pregnancy-checks" className="text-sm text-slate-500 hover:text-slate-800">
          ← Gebelik Kontrolleri
        </Link>
      </div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Toplu Gebelik Kontrolü Girişi</h1>
      <p className="mb-4 text-sm text-slate-500">
        Kontrol bekleyen (tohumlanmış, henüz sonuçlanmamış) hayvanlar aşağıda listelenir. Tarih ve kontrol yöntemini
        bir kez seçin, sadece kontrol ettiğiniz hayvanlara sonuç girin — boş bırakılan satırlar kaydedilmez.
      </p>
      <RelatedLookupsBar items={getRelatedLookups(getResource('pregnancy-checks')!)} />
      <BulkPregnancyCheckForm pendingEvents={pendingOptions} methods={methodOptions} results={resultOptions} />
    </div>
  );
}
