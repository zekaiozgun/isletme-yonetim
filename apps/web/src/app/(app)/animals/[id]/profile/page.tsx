import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { formatDateDMY } from '@/lib/format';
import { TrendLineChart, type TrendPoint } from '@/components/TrendLineChart';

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
    medicationTypes,
    dosageUnits,
    penAssignments,
    pens,
    allOffspringByMother,
    allSires,
    damBreedingEvents,
    serviceMethods,
  ] = await Promise.all([
    apiGetSafe<ApiRecord[]>('/animals/genders', []),
    apiGetSafe<ApiRecord[]>('/animals/breeds', []),
    apiGetSafe<ApiRecord[]>('/animals/statuses', []),
    apiGetSafe<ApiRecord[]>('/animals/entry-sources', []),
    apiGetSafe<ApiRecord[]>(`/weight-records/animals/${id}`, []),
    apiGetSafe<ApiRecord[]>(`/health-events/animals/${id}`, []),
    apiGetSafe<ApiRecord[]>('/health-events/event-types', []),
    apiGetSafe<ApiRecord[]>('/health-events/diseases', []),
    apiGetSafe<ApiRecord[]>('/health-events/medication-types', []),
    apiGetSafe<ApiRecord[]>('/health-events/dosage-units', []),
    apiGetSafe<ApiRecord[]>(`/pens/animals/${id}/assignments`, []),
    apiGetSafe<ApiRecord[]>('/pens', []),
    apiGetSafe<ApiRecord[]>('/reports/offspring-by-mother', []),
    apiGetSafe<ApiRecord[]>('/genetic-resource/sires', []),
    apiGetSafe<ApiRecord[]>(`/breeding-events?dam_id=${id}`, []),
    apiGetSafe<ApiRecord[]>('/breeding-events/service-methods', []),
  ]);

  // Anne/baba bilgisi - ayrı, koşullu fetch'ler (çoğu hayvanda ikisi de
  // olmayabilir, gereksiz istek atmamak için sadece FK doluysa çekilir).
  const mother = animal.mother_id ? await apiGetSafe<ApiRecord | null>(`/animals/${animal.mother_id}`, null) : null;
  const sire = animal.father_sire_id
    ? await apiGetSafe<ApiRecord | null>(`/genetic-resource/sires/${animal.father_sire_id}`, null)
    : null;
  const sireAnimal = sire?.animal_id ? await apiGetSafe<ApiRecord | null>(`/animals/${sire.animal_id}`, null) : null;

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

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <ProfileStat label="Cinsiyet" value={genderName} />
        <ProfileStat label="Irk" value={breedName} />
        <ProfileStat label="Statü" value={statusName} />
        <ProfileStat label="Yaş" value={typeof animal.age_months === 'number' ? `${animal.age_months} ay` : '—'} />
        <ProfileStat label="Doğum Tarihi" value={animal.birth_date ? formatDateDMY(animal.birth_date) : '—'} />
        <ProfileStat label="Giriş Tarihi" value={formatDateDMY(animal.entry_date)} />
        <ProfileStat label="Giriş Kaynağı" value={entrySourceName} />
        <ProfileStat
          label="Giriş Değeri"
          value={animal.entry_value !== null && animal.entry_value !== undefined ? `${String(animal.entry_value)} TL` : '—'}
        />
      </div>

      <Section title="Soy Kütüğü">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <p className="mb-1 text-xs font-medium text-slate-500">Anne</p>
            {mother ? (
              <Link href={`/animals/${mother.id}/profile`} className="text-sm font-medium text-slate-800 hover:underline">
                {String(mother.tag_number)}
                {mother.name ? ` — ${String(mother.name)}` : ''}
              </Link>
            ) : (
              <p className="text-sm text-slate-400">—</p>
            )}
          </div>
          <div>
            <p className="mb-1 text-xs font-medium text-slate-500">Baba</p>
            {sire ? (
              sireAnimal ? (
                <Link href={`/animals/${sireAnimal.id}/profile`} className="text-sm font-medium text-slate-800 hover:underline">
                  {String(sireAnimal.tag_number)} — {String(sire.name)}
                </Link>
              ) : (
                <p className="text-sm font-medium text-slate-800">
                  {sire.registry_no ? `Kayıt No ${String(sire.registry_no)} — ` : ''}
                  {String(sire.name)}
                </p>
              )
            ) : (
              <p className="text-sm text-slate-400">—</p>
            )}
          </div>
        </div>
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
                  <th className="px-3 py-2 text-left font-medium text-slate-600">İlaç</th>
                  <th className="px-3 py-2 text-left font-medium text-slate-600">Doz</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {healthEvents
                  .slice()
                  .sort((a, b) => String(b.event_date).localeCompare(String(a.event_date)))
                  .map((h) => (
                    <tr key={String(h.id)}>
                      <td className="whitespace-nowrap px-3 py-2 text-slate-700">{formatDateDMY(h.event_date)}</td>
                      <td className="whitespace-nowrap px-3 py-2 text-slate-700">{findName(healthEventTypes, h.event_type_id) ?? '—'}</td>
                      <td className="whitespace-nowrap px-3 py-2 text-slate-700">{findName(diseases, h.disease_id) ?? '—'}</td>
                      <td className="whitespace-nowrap px-3 py-2 text-slate-700">{findName(medicationTypes, h.medication_id) ?? '—'}</td>
                      <td className="whitespace-nowrap px-3 py-2 text-slate-700">
                        {h.dosage_amount !== null && h.dosage_amount !== undefined
                          ? `${String(h.dosage_amount)} ${findName(dosageUnits, h.dosage_unit_id) ?? ''}`
                          : '—'}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </Section>

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
  );
}

function ProfileStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-slate-200 p-3">
      <p className="mb-0.5 text-xs font-medium text-slate-500">{label}</p>
      <p className="text-sm font-semibold text-slate-900">{value}</p>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-6 rounded border border-slate-200 p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">{title}</h2>
      {children}
    </div>
  );
}
