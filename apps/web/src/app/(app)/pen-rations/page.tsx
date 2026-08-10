import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { formatDateDMY, formatNumberTR } from '@/lib/format';
import { deletePenRationAction } from '@/lib/actions';
import { DeleteButton } from '@/components/DeleteButton';

export default async function PenRationsPage({
  searchParams,
}: {
  searchParams: Promise<{ pen_id?: string }>;
}) {
  const [rations, pens, feedItems, units, scopes] = await Promise.all([
    apiGetSafe<ApiRecord[]>('/feed/rations', []),
    apiGetSafe<ApiRecord[]>('/pens', []),
    apiGetSafe<ApiRecord[]>('/feed/items', []),
    apiGetSafe<ApiRecord[]>('/feed/units', []),
    apiGetSafe<ApiRecord[]>('/feed/ration-item-scopes', []),
  ]);

  const penLabel = new Map(pens.map((p) => [Number(p.id), `${String(p.code)} - ${String(p.name)}`]));
  const feedItemName = new Map(feedItems.map((f) => [Number(f.id), String(f.name)]));
  const unitName = new Map(units.map((u) => [Number(u.id), String(u.name)]));
  const scopeName = new Map(scopes.map((s) => [Number(s.id), String(s.name)]));

  const sp = await searchParams;
  const selectedPenId = sp.pen_id && sp.pen_id !== '' ? Number(sp.pen_id) : undefined;

  const sorted = [...rations]
    .filter((r) => selectedPenId === undefined || Number(r.pen_id) === selectedPenId)
    .sort((a, b) => new Date(String(b.start_date)).getTime() - new Date(String(a.start_date)).getTime());

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

      <form
        method="get"
        className="mb-4 flex flex-wrap items-end gap-3 rounded border border-slate-200 bg-slate-50 p-3"
      >
        <div>
          <label htmlFor="pen_id" className="mb-1 block text-xs font-medium text-slate-600">
            Padok
          </label>
          <select
            id="pen_id"
            name="pen_id"
            defaultValue={selectedPenId ?? ''}
            className="rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900"
          >
            <option value="">Tüm Padoklar</option>
            {pens.map((p) => (
              <option key={String(p.id)} value={String(p.id)}>
                {penLabel.get(Number(p.id))}
              </option>
            ))}
          </select>
        </div>
        <button
          type="submit"
          className="rounded bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700"
        >
          Filtrele
        </button>
      </form>

      {sorted.length === 0 ? (
        <p className="text-sm text-slate-500">
          {selectedPenId === undefined ? 'Henüz rasyon kaydı yok.' : 'Bu padok için rasyon kaydı yok.'}
        </p>
      ) : (
        <div className="space-y-4">
          {sorted.map((ration) => {
            const items = Array.isArray(ration.items) ? (ration.items as ApiRecord[]) : [];
            const isActive = ration.end_date === null || ration.end_date === undefined;
            return (
              <div key={String(ration.id)} className="rounded border border-slate-200">
                <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 border-b border-slate-200 bg-slate-50 px-3 py-2">
                  <span className="font-medium text-slate-900">{penLabel.get(Number(ration.pen_id)) ?? '—'}</span>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-slate-600">
                    <span>Başlangıç: {formatDateDMY(ration.start_date)}</span>
                    <span>
                      Bitiş:{' '}
                      {isActive ? (
                        <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-800">
                          Devam Ediyor
                        </span>
                      ) : (
                        formatDateDMY(ration.end_date)
                      )}
                    </span>
                  </div>
                </div>

                {items.length === 0 ? (
                  <p className="px-3 py-2 text-sm text-slate-500">Rasyon unsuru girilmemiş.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-200 text-sm">
                      <thead className="bg-white">
                        <tr>
                          <th className="px-3 py-1.5 text-left font-medium text-slate-600">Yem Kalemi</th>
                          <th className="px-3 py-1.5 text-left font-medium text-slate-600">Miktar (hayvan başı/gün)</th>
                          <th className="px-3 py-1.5 text-left font-medium text-slate-600">Birim</th>
                          <th className="px-3 py-1.5 text-left font-medium text-slate-600">Uygulanacak Grup</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {items.map((item, index) => (
                          <tr key={index}>
                            <td className="px-3 py-1.5 text-slate-700">
                              {feedItemName.get(Number(item.feed_item_id)) ?? '—'}
                            </td>
                            <td className="px-3 py-1.5 text-slate-700">{formatNumberTR(item.daily_quantity_per_animal)}</td>
                            <td className="px-3 py-1.5 text-slate-700">{unitName.get(Number(item.unit_id)) ?? '—'}</td>
                            <td className="px-3 py-1.5 text-slate-700">{scopeName.get(Number(item.scope_id)) ?? '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 px-3 py-2">
                  <p className="text-sm text-slate-500">{ration.note ? String(ration.note) : 'Not yok'}</p>
                  <DeleteButton
                    action={deletePenRationAction.bind(null, Number(ration.id))}
                    confirmMessage="Bu rasyon kaydını kalıcı olarak silmek istediğinize emin misiniz?"
                    redirectTo="/pen-rations"
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
