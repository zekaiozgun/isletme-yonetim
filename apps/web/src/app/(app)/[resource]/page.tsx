import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { formatDateDMY } from '@/lib/format';
import { getResource } from '@/lib/resources';
import { ResourceTable } from '@/components/ResourceTable';
import { TrendLineChart, type TrendPoint } from '@/components/TrendLineChart';
import { WeightAnimalFilter } from '@/components/WeightAnimalFilter';

export default async function ResourceListPage({
  params,
  searchParams,
}: {
  params: Promise<{ resource: string }>;
  searchParams: Promise<{ animal_id?: string }>;
}) {
  const { resource: slug } = await params;
  const resource = getResource(slug);
  if (!resource) notFound();

  const isWeightRecords = resource.slug === 'weight-records';
  const sp = await searchParams;
  const animalId = isWeightRecords ? sp.animal_id : undefined;

  // include_inactive=true: bu kaynagin kendi liste sayfasinda pasif
  // (is_active=false) lookup kayitlari da gorunur olmali ki yonetilebilsin;
  // diger formlardaki secim listeleri (OptionSource) bu parametreyi
  // GONDERMEZ, o yuzden orada hala sadece aktif kayitlar teklif edilir.
  const separator = resource.listEndpoint.includes('?') ? '&' : '?';
  const query = animalId
    ? `${separator}include_inactive=true&animal_id=${encodeURIComponent(animalId)}`
    : `${separator}include_inactive=true`;
  const rows = await apiGetSafe<ApiRecord[]>(`${resource.listEndpoint}${query}`, []);

  // Tartilar listesi tek bir hayvana daraltilmissa (bkz. WeightAnimalFilter),
  // o hayvanin kilo trend grafigini listenin ustunde goster - kullanici
  // geri bildirimi: bu, "hayvan kimlik bilgisi" (sabit alanlar) yerine
  // tartinin kendi CRUD sayfasinda daha mantikli (bkz. proje hafizasi).
  const weightAnimalOptions = isWeightRecords ? await apiGetSafe<ApiRecord[]>('/animals', []) : [];
  const weightPoints: TrendPoint[] = isWeightRecords
    ? rows
        .filter((w) => typeof w.weigh_date === 'string' && typeof w.weight_kg !== 'undefined' && w.weight_kg !== null)
        .map((w) => ({ date: String(w.weigh_date), value: Number(w.weight_kg) }))
    : [];
  const firstWeight = weightPoints[0];
  const lastWeight = weightPoints[weightPoints.length - 1];
  const weightChange = firstWeight && lastWeight ? lastWeight.value - firstWeight.value : null;

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold text-slate-900">{resource.title}</h1>
        <div className="flex items-center gap-2">
          {resource.bulkEntryPath && (
            <Link
              href={resource.bulkEntryPath}
              className="rounded border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Toplu Giriş
            </Link>
          )}
          <Link
            href={`/${resource.slug}/new`}
            className="rounded bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700"
          >
            + Yeni {resource.singularTitle}
          </Link>
        </div>
      </div>
      {resource.relatedReports && resource.relatedReports.length > 0 && (
        <div className="mb-4 flex flex-wrap items-center gap-2 rounded border border-slate-200 bg-slate-50 px-3 py-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">İlgili Raporlar</span>
          {resource.relatedReports.map((report) => (
            <Link
              key={report.slug}
              href={`/reports/${report.slug}`}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700 hover:border-slate-400 hover:bg-slate-100"
            >
              {report.title}
            </Link>
          ))}
        </div>
      )}
      {isWeightRecords && (
        <>
          <WeightAnimalFilter
            animals={weightAnimalOptions.map((a) => ({
              id: String(a.id),
              label: `${String(a.tag_number)}${a.name ? ' - ' + String(a.name) : ''}`,
            }))}
            selectedId={animalId}
          />
          {animalId && (
            <div className="mb-6 rounded border border-slate-200 p-4">
              <h2 className="mb-1 text-sm font-semibold text-slate-700">Kilo Trend Grafiği</h2>
              {weightPoints.length >= 2 ? (
                <>
                  <p className="mb-3 text-sm text-slate-500">
                    {formatDateDMY(firstWeight.date)}: {firstWeight.value} kg → {formatDateDMY(lastWeight.date)}: {lastWeight.value} kg
                    {weightChange !== null && (
                      <span className={weightChange < 0 ? 'font-medium text-red-600' : 'font-medium text-emerald-700'}>
                        {' '}
                        ({weightChange >= 0 ? '+' : ''}
                        {weightChange} kg)
                      </span>
                    )}
                  </p>
                  <TrendLineChart points={weightPoints} unit="kg" />
                </>
              ) : (
                <p className="text-sm text-slate-500">
                  {weightPoints.length === 0
                    ? 'Bu hayvan için henüz tartı kaydı yok.'
                    : 'Grafik için en az 2 tartı kaydı gerekir, şu an sadece 1 kayıt var.'}
                </p>
              )}
            </div>
          )}
        </>
      )}
      <ResourceTable resource={resource} rows={rows} />
    </div>
  );
}
