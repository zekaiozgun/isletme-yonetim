import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { formatDateDMY } from '@/lib/format';
import { deletePenRationAction } from '@/lib/actions';
import { DeleteButton } from '@/components/DeleteButton';

export default async function PenRationsPage() {
  const [rations, pens, feedItems, units] = await Promise.all([
    apiGetSafe<ApiRecord[]>('/feed/rations', []),
    apiGetSafe<ApiRecord[]>('/pens', []),
    apiGetSafe<ApiRecord[]>('/feed/items', []),
    apiGetSafe<ApiRecord[]>('/feed/units', []),
  ]);

  const penLabel = new Map(pens.map((p) => [Number(p.id), `${String(p.code)} - ${String(p.name)}`]));
  const feedItemName = new Map(feedItems.map((f) => [Number(f.id), String(f.name)]));
  const unitName = new Map(units.map((u) => [Number(u.id), String(u.name)]));

  const sorted = [...rations].sort(
    (a, b) => new Date(String(b.start_date)).getTime() - new Date(String(a.start_date)).getTime()
  );

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold text-slate-900">Padok Rasyonları</h1>
        <Link
          href="/pen-rations/new"
          className="rounded bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700"
        >
          + Yeni Rasyon
        </Link>
      </div>
      <p className="mb-4 text-sm text-slate-500">
        Bir padoğa yeni rasyon girildiğinde, o padoğun önceki rasyonu otomatik olarak kapanır. Günlük yem dağıtım
        kaydı girilmez — tüketim ve maliyet, rasyon dönemi ile padoğun fiilen dolu olduğu günlerden otomatik türetilir
        (bkz. Yem Tüketim Raporu, Yem Stok Durumu).
      </p>

      {sorted.length === 0 ? (
        <p className="text-sm text-slate-500">Henüz rasyon kaydı yok.</p>
      ) : (
        <div className="overflow-x-auto rounded border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Padok</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Başlangıç</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Bitiş</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">İçerik (hayvan başına/gün)</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">Not</th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">İşlemler</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sorted.map((ration) => {
                const items = Array.isArray(ration.items) ? (ration.items as ApiRecord[]) : [];
                const content = items
                  .map(
                    (item) =>
                      `${feedItemName.get(Number(item.feed_item_id)) ?? '—'}: ${String(item.daily_quantity_per_animal)} ${unitName.get(Number(item.unit_id)) ?? ''}`
                  )
                  .join(', ');
                const isActive = ration.end_date === null || ration.end_date === undefined;
                return (
                  <tr key={String(ration.id)}>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">
                      {penLabel.get(Number(ration.pen_id)) ?? '—'}
                    </td>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">{formatDateDMY(ration.start_date)}</td>
                    <td className="whitespace-nowrap px-3 py-2 text-slate-700">
                      {isActive ? (
                        <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-800">
                          Devam Ediyor
                        </span>
                      ) : (
                        formatDateDMY(ration.end_date)
                      )}
                    </td>
                    <td className="px-3 py-2 text-slate-700">{content || '—'}</td>
                    <td className="px-3 py-2 text-slate-500">{ration.note ? String(ration.note) : '—'}</td>
                    <td className="whitespace-nowrap px-3 py-2">
                      <DeleteButton
                        action={deletePenRationAction.bind(null, Number(ration.id))}
                        confirmMessage="Bu rasyon kaydını kalıcı olarak silmek istediğinize emin misiniz?"
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
