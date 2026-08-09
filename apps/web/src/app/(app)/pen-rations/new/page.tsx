import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { RationForm } from '@/components/RationForm';

export default async function NewPenRationPage() {
  const [pens, feedItems, units, scopes] = await Promise.all([
    apiGetSafe<ApiRecord[]>('/pens', []),
    apiGetSafe<ApiRecord[]>('/feed/items', []),
    apiGetSafe<ApiRecord[]>('/feed/units', []),
    apiGetSafe<ApiRecord[]>('/feed/ration-item-scopes', []),
  ]);

  const penOptions = pens
    .map((p) => ({ id: Number(p.id), label: `${String(p.code)} - ${String(p.name)}` }))
    .sort((a, b) => a.label.localeCompare(b.label, 'tr-TR'));
  const feedItemOptions = feedItems
    .map((f) => ({ id: Number(f.id), name: String(f.name) }))
    .sort((a, b) => a.name.localeCompare(b.name, 'tr-TR'));
  const unitOptions = units.map((u) => ({ id: Number(u.id), name: String(u.name) }));
  const scopeOptions = scopes.map((s) => ({ id: Number(s.id), name: String(s.name) }));

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href="/pen-rations" className="text-sm text-slate-500 hover:text-slate-800">
          ← Padok Rasyonları
        </Link>
      </div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Yeni Padok Rasyonu</h1>
      <p className="mb-4 text-sm text-slate-500">
        Bir padok için rasyon (yem karışımı) belirleyin — miktarlar hayvan başına, günlük olarak girilir. Bu padok
        için önceden açık bir rasyon varsa, bu tarihten itibaren otomatik olarak kapanır. Anne-yavru padoklarında,
        buzağıların yetişkinlerle aynı porsiyonu yiyormuş gibi hesaplanmaması için her kalemin{' '}
        <strong>Uygulanacak Grup</strong>unu (Tüm Hayvanlar / Sadece Buzağı / Sadece Yetişkin) seçin.
      </p>
      <RationForm pens={penOptions} feedItems={feedItemOptions} units={unitOptions} scopes={scopeOptions} />
    </div>
  );
}
