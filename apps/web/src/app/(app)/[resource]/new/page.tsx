import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGet, apiGetSafe, type ApiRecord } from '@/lib/api';
import { createResource } from '@/lib/actions';
import { loadFormOptions } from '@/lib/formOptions';
import { getResource, getRelatedLookups } from '@/lib/resources';
import { ResourceForm } from '@/components/ResourceForm';
import { HealthEventForm } from '@/components/HealthEventForm';
import { RelatedLookupsBar } from '@/components/RelatedLookupsBar';
import { CrossbreedRatioCalculator } from '@/components/CrossbreedRatioCalculator';

interface MeResponse {
  role: 'YONETICI' | 'CALISAN';
}

export default async function NewResourcePage({ params }: { params: Promise<{ resource: string }> }) {
  const { resource: slug } = await params;
  const resource = getResource(slug);
  if (!resource) notFound();

  const { options, clientFields } = await loadFormOptions(resource);
  const action = createResource.bind(null, resource.slug);
  const relatedLookups = getRelatedLookups(resource);

  // Bir saglik olayinda birden fazla ilac kullanilabildigi icin (bkz.
  // kullanici geri bildirimi), health-events genel ResourceForm yerine
  // ozel bir form kullanir (bkz. components/HealthEventForm.tsx).
  if (slug === 'health-events') {
    const [animals, eventTypes, diseases, medications, dosageUnits] = await Promise.all([
      apiGetSafe<ApiRecord[]>('/animals', []),
      apiGetSafe<ApiRecord[]>('/health-events/event-types', []),
      apiGetSafe<ApiRecord[]>('/health-events/diseases', []),
      apiGetSafe<ApiRecord[]>('/health-events/medications', []),
      apiGetSafe<ApiRecord[]>('/health-events/dosage-units', []),
    ]);
    return (
      <div>
        <div className="mb-4 flex items-center gap-3">
          <Link href={`/${resource.slug}`} className="text-sm text-slate-500 hover:text-slate-800">
            ← {resource.title}
          </Link>
        </div>
        <h1 className="mb-4 text-xl font-semibold text-slate-900">Yeni {resource.singularTitle}</h1>
        <RelatedLookupsBar items={relatedLookups} />
        <HealthEventForm
          animals={animals.map((a) => ({ id: String(a.id), label: `${String(a.tag_number)}${a.name ? ' - ' + String(a.name) : ''}` }))}
          eventTypes={eventTypes.map((t) => ({ id: Number(t.id), name: String(t.name) }))}
          diseases={diseases.map((d) => ({ id: Number(d.id), name: String(d.name) }))}
          medications={medications.map((m) => ({ id: Number(m.id), name: String(m.name) }))}
          dosageUnits={dosageUnits.map((u) => ({ id: Number(u.id), name: String(u.name) }))}
        />
      </div>
    );
  }

  // Calisan modunda hayvan girisi cift onaylidir: once "Incele ve Onayla"
  // ile ozet gosterilir, kayit ancak ikinci onaydan sonra olusturulur ve
  // bu andan itibaren Calisan icin kilitlenir (bkz. app/modules/animal).
  const me = await apiGet<MeResponse>('/auth/me');
  const requireConfirmation = slug === 'animals' && me.role === 'CALISAN';

  // Bir asim (tohumlama) kaydi girilirken, secilen "Anne Adayi" o an
  // zaten "Gebe" olarak kayitliysa formu engellemeden bir uyari gosterir
  // - sistem sebebi (dusuk mu, yanlis giris mi) varsaymaz, sadece
  // celiskiyi gorunur kilar (bkz. reports.list_bred_animals).
  const warningField =
    slug === 'breeding-events'
      ? {
          fieldName: 'dam_id',
          matchValues: (await apiGetSafe<ApiRecord[]>('/reports/bred-animals', []))
            .filter((a) => a.check_status === 'Gebe')
            .map((a) => String(a.animal_id)),
          message: '⚠ Bu hayvan şu anda "Gebe" olarak kayıtlı! Yeniden tohumlamak istediğinize emin misiniz?',
        }
      : undefined;

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href={`/${resource.slug}`} className="text-sm text-slate-500 hover:text-slate-800">
          ← {resource.title}
        </Link>
      </div>
      <h1 className="mb-4 text-xl font-semibold text-slate-900">Yeni {resource.singularTitle}</h1>
      <RelatedLookupsBar items={relatedLookups} />
      {requireConfirmation && (
        <p className="mb-4 max-w-xl rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
          Bu kayıt, onayladıktan sonra sizin tarafınızdan değiştirilemez veya silinemez. Bilgileri dikkatle girin.
        </p>
      )}
      {slug === 'animals' && (
        <CrossbreedRatioCalculator
          animals={options['/animals'] ?? []}
          sires={options['/genetic-resource/sires'] ?? []}
          breeds={options['/animals/breeds'] ?? []}
        />
      )}
      <ResourceForm
        fields={clientFields}
        options={options}
        action={action}
        submitLabel={`${resource.singularTitle} Ekle`}
        requireConfirmation={requireConfirmation}
        warningField={warningField}
        redirectTo={`/${resource.slug}`}
      />
    </div>
  );
}
