import { apiGet, apiGetSafe, type ApiRecord } from '@/lib/api';
import { saveGrowthValuationCheckpointsAction } from '@/lib/valuation';
import { CHECKPOINT_ROWS, GrowthValuationCheckpointsForm } from '@/components/GrowthValuationCheckpointsForm';

interface MeResponse {
  role: 'YONETICI' | 'CALISAN';
}

function formatTry(value: string): string {
  if (value === '') return '—';
  const n = Number(value);
  return Number.isFinite(n) ? `${n.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} TL` : '—';
}

export default async function GrowthValuationCheckpointsPage() {
  const [me, genders] = await Promise.all([apiGet<MeResponse>('/auth/me'), apiGetSafe<ApiRecord[]>('/animals/genders', [])]);
  const erkekId = Number(genders.find((g) => g.code === 'ERKEK')?.id ?? 0);
  const disiId = Number(genders.find((g) => g.code === 'DISI')?.id ?? 0);

  const checkpoints = await apiGetSafe<ApiRecord[]>('/growth-valuation-checkpoints', []);
  const values: Record<string, string> = {};
  for (const cp of checkpoints) {
    const prefix = Number(cp.gender_id) === erkekId ? 'erkek' : 'disi';
    values[`${prefix}_${String(cp.category_code)}`] = String(cp.value_try ?? '');
  }

  const description =
    'Malzeme durumundaki (henüz Demirbaşa geçmemiş) genç hayvanların ve olgun dişilerin tahmini piyasa değerini hesaplamak için kullanılan referans fiyatlar. USD karşılığı raporlarda ilgili tarihteki TCMB kuruyla otomatik hesaplanır. Boş bırakılan hücreler değerlendirmeye katılmaz.';

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Büyüme Değerleme Çıpaları</h1>
      <p className="mb-4 max-w-2xl text-sm text-slate-500">
        {description} {me.role !== 'YONETICI' && 'Bu değerleri sadece yönetici düzenleyebilir.'}
      </p>
      {me.role === 'YONETICI' ? (
        <GrowthValuationCheckpointsForm action={saveGrowthValuationCheckpointsAction.bind(null, erkekId, disiId)} values={values} />
      ) : (
        <div className="max-w-2xl overflow-x-auto rounded border border-slate-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-slate-600">
                <th className="px-3 py-2 font-medium">Kategori</th>
                <th className="px-3 py-2 font-medium">Erkek</th>
                <th className="px-3 py-2 font-medium">Dişi</th>
              </tr>
            </thead>
            <tbody>
              {CHECKPOINT_ROWS.map((row) => (
                <tr key={row.code} className="border-b border-slate-100 last:border-0">
                  <td className="px-3 py-2 text-slate-700">{row.label}</td>
                  <td className="px-3 py-2 text-slate-700">{row.femaleOnly ? <span className="text-slate-300">—</span> : formatTry(values[`erkek_${row.code}`] ?? '')}</td>
                  <td className="px-3 py-2 text-slate-700">{formatTry(values[`disi_${row.code}`] ?? '')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
