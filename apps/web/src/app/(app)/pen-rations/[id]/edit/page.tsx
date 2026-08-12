import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { getResource } from '@/lib/resources';
import { RationForm, type RationFormInitial } from '@/components/RationForm';
import { RelatedLookupsBar } from '@/components/RelatedLookupsBar';

const RATION_RELATED_LOOKUPS = ['feed-items', 'feed-units']
  .map((slug) => getResource(slug))
  .filter((r): r is NonNullable<typeof r> => r !== undefined)
  .map((r) => ({ slug: r.slug, title: r.title }));

export default async function EditPenRationPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const [ration, pens, feedItems, units, scopes] = await Promise.all([
    apiGetSafe<ApiRecord | null>(`/feed/rations/${id}`, null),
    apiGetSafe<ApiRecord[]>('/pens', []),
    apiGetSafe<ApiRecord[]>('/feed/items', []),
    apiGetSafe<ApiRecord[]>('/feed/units', []),
    apiGetSafe<ApiRecord[]>('/feed/ration-item-scopes', []),
  ]);
  if (!ration) notFound();

  const penOptions = pens
    .map((p) => ({ id: Number(p.id), label: `${String(p.code)} - ${String(p.name)}` }))
    .sort((a, b) => a.label.localeCompare(b.label, 'tr-TR'));
  const feedItemOptions = feedItems
    .map((f) => ({ id: Number(f.id), name: String(f.name) }))
    .sort((a, b) => a.name.localeCompare(b.name, 'tr-TR'));
  const unitOptions = units.map((u) => ({ id: Number(u.id), name: String(u.name) }));
  const scopeOptions = scopes.map((s) => ({ id: Number(s.id), name: String(s.name) }));

  const items = Array.isArray(ration.items) ? (ration.items as ApiRecord[]) : [];
  const initial: RationFormInitial = {
    penId: String(ration.pen_id),
    startDate: String(ration.start_date),
    note: ration.note ? String(ration.note) : '',
    items: items.map((item) => ({
      feedItemId: String(item.feed_item_id),
      dailyQuantityPerAnimal: String(Number(item.daily_quantity_per_animal)),
      unitId: String(item.unit_id),
      scopeId: String(item.scope_id),
    })),
  };

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href="/pen-rations" className="text-sm text-slate-500 hover:text-slate-800">
          ← Padok Rasyonları
        </Link>
      </div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Padok Rasyonunu Düzenle</h1>
      <p className="mb-4 text-sm text-slate-500">
        Bu, dönem geçişi (önceki rasyonu otomatik kapatma) tetiklemez — sadece bu kaydın kendisini düzeltir. Yeni bir
        dönem başlatmak için &quot;Padok Rasyonları&quot; sayfasından &quot;+ Yeni Rasyon&quot; kullanın.
      </p>
      <RelatedLookupsBar items={RATION_RELATED_LOOKUPS} />
      <RationForm
        pens={penOptions}
        feedItems={feedItemOptions}
        units={unitOptions}
        scopes={scopeOptions}
        rationId={Number(id)}
        initial={initial}
      />
    </div>
  );
}
