import Link from 'next/link';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { groupedResources } from '@/lib/resources';
import { StatTile } from '@/components/StatTile';

function asNumber(value: unknown): number {
  return typeof value === 'number' ? value : 0;
}

function formatPercent(value: unknown): string {
  return typeof value === 'number' ? `%${value}` : '—';
}

export default async function Home() {
  const groups = groupedResources();

  const [summary, inventory, penOccupancy] = await Promise.all([
    apiGetSafe<ApiRecord>('/reports/dashboard-summary', {}),
    apiGetSafe<ApiRecord>('/reports/herd-inventory', {}),
    apiGetSafe<ApiRecord[]>('/reports/pen-occupancy', []),
  ]);

  const checkDueCount = asNumber(summary.pregnancy_check_due_count);
  const repeatBreederCount = asNumber(summary.repeat_breeder_count);
  const occupancyRate = typeof summary.pen_occupancy_rate === 'number' ? summary.pen_occupancy_rate : null;

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold text-slate-900">Dashboard</h1>
      <p className="mb-6 text-slate-500">Sürünün güncel durumu ve dikkat gerektiren kayıtlar.</p>

      <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <StatTile label="Aktif Hayvan Sayısı" value={String(asNumber(summary.active_animal_count))} href="/animals" />
        <StatTile
          label="Tohumlanacak Hayvan"
          value={String(asNumber(summary.breeding_candidate_count))}
          href="/reports/breeding-candidates"
        />
        <StatTile
          label="Gebelik Kontrolü Gereken"
          value={String(checkDueCount)}
          href="/reports/bred-animals"
          status={checkDueCount > 0 ? 'warning' : 'neutral'}
        />
        <StatTile label="Gebe Hayvan" value={String(asNumber(summary.pregnant_count))} href="/reports/pregnant-animals" />
        <StatTile
          label="Tekrar Kızgınlık / Boş"
          value={String(repeatBreederCount)}
          href="/reports/repeat-breeders"
          status={repeatBreederCount > 0 ? 'warning' : 'neutral'}
        />
        <StatTile label="Buzağı (0-7 Ay)" value={String(asNumber(summary.calves_count))} href="/reports/calves" />
        <StatTile label="Düve ve Dana (7-12 Ay)" value={String(asNumber(summary.heifers_steers_count))} href="/reports/heifers-steers" />
        <StatTile
          label="Padok Doluluk Oranı"
          value={formatPercent(occupancyRate)}
          href="/reports/pen-occupancy"
          status={occupancyRate !== null && occupancyRate >= 100 ? 'critical' : 'neutral'}
        />
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded border border-slate-200 p-4">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Sürü Dağılımı</h2>
          <dl className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <dt className="text-slate-600">Dişi (Aktif)</dt>
              <dd className="font-medium text-slate-900">{asNumber(inventory.female_active)}</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-slate-600">Erkek (Aktif)</dt>
              <dd className="font-medium text-slate-900">{asNumber(inventory.male_active)}</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-slate-600">Tohumlanacak Yaşta Dişi (12+ ay)</dt>
              <dd className="font-medium text-slate-900">{asNumber(inventory.breeding_age_female_count)}</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-slate-600">Yetişkin Erkek (12+ ay)</dt>
              <dd className="font-medium text-slate-900">{asNumber(inventory.adult_male_count)}</dd>
            </div>
          </dl>
        </div>

        <div className="rounded border border-slate-200 p-4">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Padok Doluluk</h2>
          {penOccupancy.length === 0 ? (
            <p className="text-sm text-slate-500">Henüz padok kaydı yok.</p>
          ) : (
            <div className="space-y-2.5">
              {penOccupancy.slice(0, 6).map((pen) => {
                const rate = typeof pen.occupancy_rate === 'number' ? pen.occupancy_rate : null;
                const fillWidth = rate !== null ? Math.min(rate, 100) : 0;
                const fillColor = rate !== null && rate >= 100 ? 'bg-red-500' : rate !== null && rate >= 85 ? 'bg-amber-500' : 'bg-slate-600';
                return (
                  <div key={String(pen.pen_id)} className="text-sm">
                    <div className="mb-1 flex items-center justify-between">
                      <span className="text-slate-700">
                        {String(pen.code)} — {String(pen.name)}
                      </span>
                      <span className="text-slate-500">
                        {String(pen.current_count)}/{pen.capacity !== null && pen.capacity !== undefined ? String(pen.capacity) : '—'}
                      </span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                      <div className={`h-full rounded-full ${fillColor}`} style={{ width: `${fillWidth}%` }} />
                    </div>
                  </div>
                );
              })}
              <Link href="/reports/pen-occupancy" className="mt-1 inline-block text-xs font-medium text-slate-600 hover:underline">
                Tüm padokları gör →
              </Link>
            </div>
          )}
        </div>
      </div>

      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Hızlı Erişim</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((group) => (
          <div key={group.group} className="rounded border border-slate-200 p-4">
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">{group.group}</h3>
            <ul className="space-y-1">
              {group.items.map((resource) => (
                <li key={resource.slug}>
                  <Link href={`/${resource.slug}`} className="text-sm text-slate-700 hover:text-slate-900 hover:underline">
                    {resource.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
