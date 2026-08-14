import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { formatDateDMY, formatCurrencyTRY, formatUsdValue, formatNumberTR } from '@/lib/format';
import { formatValuationStatus, formatSourceCode } from '@/lib/reports';
import { TrendLineChart, type TrendPoint } from '@/components/TrendLineChart';
import { PedigreeTree, flattenPedigreeTree } from '@/components/PedigreeTree';
import { PdfExportButton } from '@/components/PdfExportButton';

function findName(list: ApiRecord[], id: unknown): string | null {
  const item = list.find((i) => String(i.id) === String(id));
  return item ? String(item.name) : null;
}

/** Hayvan Profili - tek bir hayvanla ilgili kimlik, soy kütüğü, kilo
 * trendi, üreme geçmişi, sağlık ve padok geçmişini TEK sayfada toplayan
 * salt-okunur bir görünüm. Hayvan Bilgisi (düzenleme) formundan bilinçli
 * olarak AYRI: o form sabit/nadiren değişen kimlik alanları içindir,
 * burası zamanla biriken/türetilen veriler içindir (kullanıcı geri
 * bildirimi - bkz. proje hafızası). Hiçbir yeni backend uç noktası
 * gerekmedi - hepsi zaten var olan hayvan-bazlı filtreleme desteğinden
 * (weight-records, health-events, pens, breeding-events) besleniyor;
 * soy kütüğü listeleri (offspring-by-mother/sire) TAM listeyi çekip
 * gerçek FK (mother_id/sire_id) ile client-side filtrelenir - metin
 * arama (q=) burada KULLANILMAZ çünkü bu hayvanın kendi küpe numarası,
 * başka bir hayvanın yavru kaydında da metinsel olarak geçebilir
 * (yanlış eşleşme riski). */
export default async function AnimalProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const animal = await apiGetSafe<ApiRecord | null>(`/animals/${id}`, null);
  if (!animal) notFound();

  const [
    genders,
    breeds,
    statuses,
    entrySources,
    weightRecords,
    healthEvents,
    healthEventTypes,
    diseases,
    penAssignments,
    pens,
    allOffspringByMother,
    allSires,
    damBreedingEvents,
    serviceMethods,
    evaluations,
    evaluationReasons,
    evaluationPriorities,
    valuation,
  ] = await Promise.all([
    apiGetSafe<ApiRecord[]>('/animals/genders', []),
    apiGetSafe<ApiRecord[]>('/animals/breeds', []),
    apiGetSafe<ApiRecord[]>('/animals/statuses', []),
    apiGetSafe<ApiRecord[]>('/animals/entry-sources', []),
    apiGetSafe<ApiRecord[]>(`/weight-records/animals/${id}`, []),
    apiGetSafe<ApiRecord[]>(`/health-events/animals/${id}`, []),
    apiGetSafe<ApiRecord[]>('/health-events/event-types', []),
    apiGetSafe<ApiRecord[]>('/health-events/diseases', []),
    apiGetSafe<ApiRecord[]>(`/pens/animals/${id}/assignments`, []),
    apiGetSafe<ApiRecord[]>('/pens', []),
    apiGetSafe<ApiRecord[]>('/reports/offspring-by-mother', []),
    apiGetSafe<ApiRecord[]>('/genetic-resource/sires', []),
    apiGetSafe<ApiRecord[]>(`/breeding-events?dam_id=${id}`, []),
    apiGetSafe<ApiRecord[]>('/breeding-events/service-methods', []),
    apiGetSafe<ApiRecord[]>(`/evaluations/animals/${id}`, []),
    apiGetSafe<ApiRecord[]>('/evaluations/reasons', []),
    apiGetSafe<ApiRecord[]>('/evaluations/priorities', []),
    apiGetSafe<ApiRecord | null>(`/reports/animal-valuation/${id}`, null),
  ]);

  // Soy ağacı (3 nesil: anne/baba + anneanne/dede vb.) - tek uç noktadan,
  // hiçbir yerde saklanmaz (bkz. components/PedigreeTree.tsx).
  const pedigree = await apiGetSafe<ApiRecord | null>(`/animals/${id}/pedigree?generations=3`, null);
  const pedigreeRows = flattenPedigreeTree(pedigree);

  // Bu hayvan kendisi bir boğa (Sire) olarak kayıtlıysa (sürüye ait,
  // damızlık kullanılmış olabilir), kendi yavrularını da gösterelim.
  const selfAsSire = allSires.find((s) => String(s.animal_id) === String(id));
  const offspringAsMother = allOffspringByMother.filter((o) => String(o.mother_id) === String(id));
  const offspringAsSire = selfAsSire
    ? await apiGetSafe<ApiRecord[]>('/reports/offspring-by-sire', []).then((all) =>
        all.filter((o) => String(o.sire_id) === String(selfAsSire.id))
      )
    : [];

  const weightPoints: TrendPoint[] = weightRecords
    .filter((w) => typeof w.weigh_date === 'string' && typeof w.weight_kg !== 'undefined' && w.weight_kg !== null)
    .map((w) => ({ date: String(w.weigh_date), value: Number(w.weight_kg) }));
  const firstWeight = weightPoints[0];
  const lastWeight = weightPoints[weightPoints.length - 1];
  const weightChange = firstWeight && lastWeight ? lastWeight.value - firstWeight.value : null;

  const genderName = findName(genders, animal.gender_id) ?? '—';
  const breedName = findName(breeds, animal.breed_id) ?? '—';
  const statusName = findName(statuses, animal.status_id) ?? '—';
  const entrySourceName = findName(entrySources, animal.entry_source_id) ?? '—';

  const penMap = new Map(pens.map((p) => [String(p.id), `${String(p.code)} - ${String(p.name)}`]));

  const isActiveStatus = statusName === 'Aktif';
  const deltaPercent =
    valuation && valuation.entry_value_try !== null && valuation.entry_value_try !== undefined && Number(valuation.entry_value_try) !== 0
      ? ((Number(valuation.current_value_try) - Number(valuation.entry_value_try)) / Number(valuation.entry_value_try)) * 100
      : null;

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href="/animals" className="text-sm text-slate-500 hover:text-slate-800">
          ← Hayvanlar
        </Link>
      </div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-semibold text-slate-900">
          {String(animal.tag_number)}
          {animal.name ? ` — ${String(animal.name)}` : ''}
        </h1>
        <Link
          href={`/animals/${id}`}
          className="rounded border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Kaydı Düzenle
        </Link>
      </div>

      <div className="mb-2 flex flex-wrap gap-1.5">
        <Chip>{genderName}</Chip>
        <Chip>{breedName}</Chip>
        <Chip tone={isActiveStatus ? 'success' : 'neutral'}>{statusName}</Chip>
        <Chip>{typeof animal.age_months === 'number' ? `${animal.age_months} ay` : '—'}</Chip>
      </div>
      <p className="mb-5 text-xs text-slate-400">
        Doğum {animal.birth_date ? formatDateDMY(animal.birth_date) : '—'}
        {' · '}Giriş {formatDateDMY(animal.entry_date)}
        {' · '}
        {entrySourceName}
      </p>

      <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-200 p-3.5">
          <p className="mb-0.5 text-xs font-medium text-slate-500">Edinme Değeri</p>
          <p className="text-lg font-semibold text-slate-900">
            {valuation && valuation.entry_value_try !== null && valuation.entry_value_try !== undefined
              ? formatCurrencyTRY(valuation.entry_value_try)
              : '—'}
          </p>
          <p className="mt-0.5 text-xs text-slate-400">
            {valuation && valuation.entry_value_usd !== null && valuation.entry_value_usd !== undefined
              ? `≈ ${formatUsdValue(valuation.entry_value_usd)} · `
              : ''}
            {animal.entry_date ? `${formatDateDMY(animal.entry_date)} kuru` : ''}
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-3.5">
          <div className="flex items-baseline justify-between">
            <p className="mb-0.5 text-xs font-medium text-slate-500">Güncel Tahmini Değer</p>
            {deltaPercent !== null && (
              <span className={`text-xs font-semibold ${deltaPercent < 0 ? 'text-red-600' : 'text-emerald-700'}`}>
                {deltaPercent > 0 ? '+' : deltaPercent < 0 ? '-' : ''}%{formatNumberTR(Math.abs(deltaPercent), 1)}
              </span>
            )}
          </div>
          <p className="text-lg font-semibold text-slate-900">{valuation ? formatCurrencyTRY(valuation.current_value_try) : '—'}</p>
          <p className="mt-0.5 text-xs text-slate-400">
            {valuation ? `≈ ${formatUsdValue(valuation.current_value_usd)} · ` : ''}
            {valuation
              ? `${formatValuationStatus(valuation.current_value_status_code)} · ${formatSourceCode(valuation.current_value_source_code)}`
              : ''}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="flex flex-col gap-6">
          <Section title="Soy Kütüğü">
            {pedigreeRows.length > 1 && (
              <div className="mb-3 flex justify-end print:hidden">
                <PdfExportButton
                  title={`${String(animal.tag_number)} — Soy Kütüğü Belgesi`}
                  columns={[
                    { label: 'Nesil', width: 'narrow' },
                    { label: 'İlişki', width: 'narrow' },
                    { label: 'Küpe No / Kimlik', width: 'narrow' },
                    { label: 'Ad', width: 'narrow' },
                    { label: 'Irk', width: 'narrow' },
                    { label: 'Melez Oranı', width: 'narrow' },
                  ]}
                  rows={pedigreeRows.map((r) => [
                    String(r.generation),
                    r.relation,
                    r.tagNumber,
                    r.name,
                    r.breedName,
                    r.ratio,
                  ])}
                  filename={`${String(animal.tag_number)}-soy-kutugu.pdf`}
                />
              </div>
            )}
            <PedigreeTree node={pedigree} />
            {(offspringAsMother.length > 0 || offspringAsSire.length > 0) && (
              <div className="mt-4">
                <p className="mb-1 text-xs font-medium text-slate-500">
                  Yavruları ({offspringAsMother.length + offspringAsSire.length})
                </p>
                <ul className="space-y-1 text-sm">
                  {[...offspringAsMother, ...offspringAsSire].map((o) => (
                    <li key={String(o.animal_id)}>
                      <Link href={`/animals/${o.animal_id}/profile`} className="text-slate-700 hover:underline">
                        {String(o.tag_number)}
                      </Link>{' '}
                      <span className="text-slate-400">({formatDateDMY(o.birth_date)})</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {selfAsSire && offspringAsMother.length === 0 && offspringAsSire.length === 0 && (
              <p className="mt-4 text-sm text-slate-500">Bu hayvan bir damızlık boğa olarak kayıtlı, henüz yavrusu yok.</p>
            )}
          </Section>

          {damBreedingEvents.length > 0 && (
            <Section title="Üreme Geçmişi">
              <div className="overflow-x-auto rounded border border-slate-200">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Tohumlama Tarihi</th>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Yöntem</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {damBreedingEvents
                      .slice()
                      .sort((a, b) => String(b.service_date).localeCompare(String(a.service_date)))
                      .map((b) => (
                        <tr key={String(b.id)}>
                          <td className="whitespace-nowrap px-3 py-2 text-slate-700">{formatDateDMY(b.service_date)}</td>
                          <td className="whitespace-nowrap px-3 py-2 text-slate-700">{findName(serviceMethods, b.service_method_id) ?? '—'}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </Section>
          )}

          <Section title="Padok Geçmişi">
            {penAssignments.length === 0 ? (
              <p className="text-sm text-slate-500">Padok kaydı yok.</p>
            ) : (
              <div className="overflow-x-auto rounded border border-slate-200">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Padok</th>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Başlangıç</th>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Bitiş</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {penAssignments
                      .slice()
                      .sort((a, b) => String(b.assigned_date).localeCompare(String(a.assigned_date)))
                      .map((a) => (
                        <tr key={String(a.id)}>
                          <td className="whitespace-nowrap px-3 py-2 text-slate-700">{penMap.get(String(a.pen_id)) ?? `#${String(a.pen_id)}`}</td>
                          <td className="whitespace-nowrap px-3 py-2 text-slate-700">{formatDateDMY(a.assigned_date)}</td>
                          <td className="whitespace-nowrap px-3 py-2 text-slate-700">{a.removed_date ? formatDateDMY(a.removed_date) : 'Halen'}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </Section>
        </div>

        <div className="flex flex-col gap-6">
          <Section title="Kilo Trend Grafiği">
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
                {weightPoints.length === 0 ? 'Henüz tartı kaydı yok.' : 'Grafik için en az 2 tartı kaydı gerekir.'}{' '}
                <Link href={`/weight-records?animal_id=${id}`} className="font-medium text-slate-700 hover:underline">
                  Tartılara git →
                </Link>
              </p>
            )}
          </Section>

          <Section title="Sağlık Geçmişi">
            {healthEvents.length === 0 ? (
              <p className="text-sm text-slate-500">Sağlık olayı kaydı yok.</p>
            ) : (
              <div className="overflow-x-auto rounded border border-slate-200">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Tarih</th>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Olay Tipi</th>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Hastalık/Tanı</th>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">İlaçlar</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {healthEvents
                      .slice()
                      .sort((a, b) => String(b.event_date).localeCompare(String(a.event_date)))
                      .map((h) => {
                        const meds = Array.isArray(h.medications) ? (h.medications as ApiRecord[]) : [];
                        const medsText =
                          meds.length === 0
                            ? '—'
                            : meds
                                .map((m) =>
                                  m.dosage_amount !== null && m.dosage_amount !== undefined
                                    ? `${String(m.medication_name)} (${String(m.dosage_amount)}${m.dosage_unit_name ? ' ' + String(m.dosage_unit_name) : ''})`
                                    : String(m.medication_name)
                                )
                                .join(', ');
                        return (
                          <tr key={String(h.id)}>
                            <td className="whitespace-nowrap px-3 py-2 text-slate-700">{formatDateDMY(h.event_date)}</td>
                            <td className="whitespace-nowrap px-3 py-2 text-slate-700">{findName(healthEventTypes, h.event_type_id) ?? '—'}</td>
                            <td className="whitespace-nowrap px-3 py-2 text-slate-700">{findName(diseases, h.disease_id) ?? '—'}</td>
                            <td className="px-3 py-2 text-slate-700">{medsText}</td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>
            )}
          </Section>

          <Section title="Değerlendirme Geçmişi">
            {evaluations.length === 0 ? (
              <p className="text-sm text-slate-500">Değerlendirme kaydı yok.</p>
            ) : (
              <div className="overflow-x-auto rounded border border-slate-200">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Tarih</th>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Neden</th>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Öncelik</th>
                      <th className="px-3 py-2 text-left font-medium text-slate-600">Not</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {evaluations
                      .slice()
                      .sort((a, b) => String(b.evaluation_date).localeCompare(String(a.evaluation_date)))
                      .map((e) => (
                        <tr key={String(e.id)}>
                          <td className="whitespace-nowrap px-3 py-2 text-slate-700">{formatDateDMY(e.evaluation_date)}</td>
                          <td className="whitespace-nowrap px-3 py-2 text-slate-700">{findName(evaluationReasons, e.reason_id) ?? '—'}</td>
                          <td className="whitespace-nowrap px-3 py-2 text-slate-700">{findName(evaluationPriorities, e.priority_id) ?? '—'}</td>
                          <td className="px-3 py-2 text-slate-700">{e.note ? String(e.note) : '—'}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </Section>
        </div>
      </div>
    </div>
  );
}

function Chip({ children, tone = 'neutral' }: { children: React.ReactNode; tone?: 'neutral' | 'success' }) {
  const toneClass = tone === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-700';
  return <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${toneClass}`}>{children}</span>;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-6 rounded border border-slate-200 p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">{title}</h2>
      {children}
    </div>
  );
}
