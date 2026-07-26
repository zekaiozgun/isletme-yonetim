import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { saveGrowthValuationCheckpointsAction } from '@/lib/valuation';
import { GrowthValuationCheckpointsForm } from '@/components/GrowthValuationCheckpointsForm';

export default async function GrowthValuationCheckpointsPage() {
  const genders = await apiGetSafe<ApiRecord[]>('/animals/genders', []);
  const erkekId = Number(genders.find((g) => g.code === 'ERKEK')?.id ?? 0);
  const disiId = Number(genders.find((g) => g.code === 'DISI')?.id ?? 0);

  const checkpoints = await apiGetSafe<ApiRecord[]>('/growth-valuation-checkpoints', []);
  const values: Record<string, string> = {};
  for (const cp of checkpoints) {
    const prefix = Number(cp.gender_id) === erkekId ? 'erkek' : 'disi';
    values[`${prefix}_${String(cp.category_code)}`] = String(cp.value_try ?? '');
  }

  const action = saveGrowthValuationCheckpointsAction.bind(null, erkekId, disiId);

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Büyüme Değerleme Çıpaları</h1>
      <p className="mb-4 max-w-2xl text-sm text-slate-500">
        Malzeme durumundaki (henüz Demirbaşa geçmemiş) genç hayvanların ve olgun dişilerin tahmini piyasa değerini
        hesaplamak için kullanılan referans fiyatlar. Değerleri TL olarak girin - USD karşılığı raporlarda ilgili
        tarihteki TCMB kuruyla otomatik hesaplanır. Boş bırakılan hücreler değerlendirmeye katılmaz.
      </p>
      <GrowthValuationCheckpointsForm action={action} values={values} />
    </div>
  );
}
