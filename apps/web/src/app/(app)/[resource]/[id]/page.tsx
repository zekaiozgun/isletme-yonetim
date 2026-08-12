import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGet, apiGetSafe, type ApiRecord } from '@/lib/api';
import { cancelAnimalEntryAction, deleteResource, updateResource } from '@/lib/actions';
import { loadFormOptions } from '@/lib/formOptions';
import { getResource, getRelatedLookups } from '@/lib/resources';
import { ResourceForm } from '@/components/ResourceForm';
import { DeleteButton } from '@/components/DeleteButton';
import { CancelEntryButton } from '@/components/CancelEntryButton';
import { HealthEventForm, type HealthEventFormInitial } from '@/components/HealthEventForm';
import { RelatedLookupsBar } from '@/components/RelatedLookupsBar';

interface MeResponse {
  role: 'YONETICI' | 'CALISAN';
}

// Hayvan silme yalnizca YONETICI'ye acik (diger kaynaklarda kisitlama yok).
// Backend'de de ayni kural DELETE /animals/{id}'de zorunlu kilinir - burasi
// sadece UI'da gereksiz bir butonu gostermemek icin.
function canDeleteResource(resourceSlug: string, role: MeResponse['role']): boolean {
  if (resourceSlug === 'animals') return role === 'YONETICI';
  return true;
}

export default async function EditResourcePage({ params }: { params: Promise<{ resource: string; id: string }> }) {
  const { resource: slug, id } = await params;
  const resource = getResource(slug);
  if (!resource) notFound();

  const record = await apiGetSafe<ApiRecord | null>(`${resource.listEndpoint}/${id}`, null);
  if (!record) notFound();

  const me = await apiGet<MeResponse>('/auth/me');
  const { options, clientFields } = await loadFormOptions(resource, record);
  const updateAction = updateResource.bind(null, resource.slug, id);
  const deleteAction = deleteResource.bind(null, resource.slug, id);
  const cancelEntryAction = cancelAnimalEntryAction.bind(null, id);

  // Calisan'in cift onayla olusturdugu kilitli (is_locked) hayvan kaydi,
  // kendisi tarafindan ne degistirilebilir ne de silinebilir - tek duzeltme
  // yolu asagidaki "Hatali Giris Iptali"dir (bkz. app/modules/animal
  // service.cancel_animal_entry). YONETICI icin kilit hicbir zaman gecerli
  // degildir (kullanici tercihiyle: "Sadece Calisan'a kilit").
  const isAnimal = resource.slug === 'animals';
  const isLockedForCalisan = isAnimal && Boolean(record.is_locked) && me.role === 'CALISAN';
  const relatedLookups = getRelatedLookups(resource);

  // bkz. [resource]/new/page.tsx aynı not - health-events çoklu ilaç
  // desteği için özel form kullanır.
  if (resource.slug === 'health-events') {
    const [animals, eventTypes, diseases, medications, dosageUnits] = await Promise.all([
      apiGetSafe<ApiRecord[]>('/animals', []),
      apiGetSafe<ApiRecord[]>('/health-events/event-types', []),
      apiGetSafe<ApiRecord[]>('/health-events/diseases', []),
      apiGetSafe<ApiRecord[]>('/health-events/medications', []),
      apiGetSafe<ApiRecord[]>('/health-events/dosage-units', []),
    ]);
    const recordMedications = Array.isArray(record.medications) ? (record.medications as ApiRecord[]) : [];
    const initial: HealthEventFormInitial = {
      animalId: String(record.animal_id),
      eventTypeId: String(record.event_type_id),
      eventDate: String(record.event_date),
      diseaseId: record.disease_id !== null && record.disease_id !== undefined ? String(record.disease_id) : '',
      veterinarianNote: record.veterinarian_note ? String(record.veterinarian_note) : '',
      cost: record.cost !== null && record.cost !== undefined ? String(record.cost) : '',
      note: record.note ? String(record.note) : '',
      medications: recordMedications.map((med) => ({
        medicationId: String(med.medication_id),
        dosageAmount: med.dosage_amount !== null && med.dosage_amount !== undefined ? String(med.dosage_amount) : '',
        dosageUnitId: med.dosage_unit_id !== null && med.dosage_unit_id !== undefined ? String(med.dosage_unit_id) : '',
      })),
    };
    return (
      <div>
        <div className="mb-4 flex items-center gap-3">
          <Link href={`/${resource.slug}`} className="text-sm text-slate-500 hover:text-slate-800">
            ← {resource.title}
          </Link>
        </div>
        <h1 className="mb-4 text-xl font-semibold text-slate-900">{resource.singularTitle} Düzenle</h1>
        <RelatedLookupsBar items={relatedLookups} />
        <HealthEventForm
          animals={animals.map((a) => ({ id: String(a.id), label: `${String(a.tag_number)}${a.name ? ' - ' + String(a.name) : ''}` }))}
          eventTypes={eventTypes.map((t) => ({ id: Number(t.id), name: String(t.name) }))}
          diseases={diseases.map((d) => ({ id: Number(d.id), name: String(d.name) }))}
          medications={medications.map((m) => ({ id: Number(m.id), name: String(m.name) }))}
          dosageUnits={dosageUnits.map((u) => ({ id: Number(u.id), name: String(u.name) }))}
          eventId={id}
          initial={initial}
        />
        <div className="mt-8 max-w-xl border-t border-slate-200 pt-6">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Tehlikeli Bölge</h2>
          <p className="mb-3 text-sm text-slate-500">
            Bu sağlık olayı kaydını kalıcı olarak siler.
          </p>
          <DeleteButton
            action={deleteAction}
            confirmMessage="Bu sağlık olayı kaydını silmek istediğinize emin misiniz?"
            redirectTo="/health-events"
          />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href={`/${resource.slug}`} className="text-sm text-slate-500 hover:text-slate-800">
          ← {resource.title}
        </Link>
      </div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-semibold text-slate-900">{resource.singularTitle} Düzenle</h1>
        {isAnimal && (
          <Link href={`/animals/${id}/profile`} className="text-sm font-medium text-slate-600 hover:text-slate-900 hover:underline">
            Profili Gör →
          </Link>
        )}
      </div>
      <RelatedLookupsBar items={relatedLookups} />

      {isLockedForCalisan && (
        <p className="mb-4 max-w-xl rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
          Bu kayıt onaylanmış ve kilitlenmiş; değiştiremez veya silemezsiniz. Hatalı giriş ise aşağıdaki
          &quot;Hatalı Giriş İptali&quot; ile pasife alabilirsiniz.
        </p>
      )}

      <ResourceForm
        fields={clientFields}
        options={options}
        action={updateAction}
        submitLabel="Kaydet"
        initialValues={record}
        readOnly={isLockedForCalisan}
        redirectTo={`/${resource.slug}`}
      />

      {!isLockedForCalisan && canDeleteResource(resource.slug, me.role) && (
        <div className="mt-8 max-w-xl border-t border-slate-200 pt-6">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Tehlikeli Bölge</h2>
          <p className="mb-3 text-sm text-slate-500">
            Bu {resource.singularTitle.toLowerCase()} kaydını kalıcı olarak siler. Başka kayıtlarca kullanılıyorsa
            silme işlemi engellenir.
          </p>
          <DeleteButton
            action={deleteAction}
            confirmMessage={`Bu ${resource.singularTitle.toLowerCase()} kaydını silmek istediğinize emin misiniz?`}
            redirectTo={`/${resource.slug}`}
          />
        </div>
      )}

      {isAnimal && (
        <div className="mt-8 max-w-xl border-t border-slate-200 pt-6">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Hatalı Giriş</h2>
          <p className="mb-3 text-sm text-slate-500">
            Bu kayıt yanlış girildiyse, silmek yerine statüsünü &quot;Hatalı Giriş İptali&quot; yaparak pasife alın.
          </p>
          <CancelEntryButton
            action={cancelEntryAction}
            confirmMessage="Bu hayvan kaydını 'Hatalı Giriş İptali' statüsüne alarak pasife almak istediğinize emin misiniz?"
            redirectTo="/animals"
          />
        </div>
      )}
    </div>
  );
}
