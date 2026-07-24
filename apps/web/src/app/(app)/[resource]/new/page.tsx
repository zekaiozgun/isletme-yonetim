import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGet, apiGetSafe, type ApiRecord } from '@/lib/api';
import { createResource } from '@/lib/actions';
import { loadFormOptions } from '@/lib/formOptions';
import { getResource } from '@/lib/resources';
import { ResourceForm } from '@/components/ResourceForm';

interface MeResponse {
  role: 'YONETICI' | 'CALISAN';
}

export default async function NewResourcePage({ params }: { params: Promise<{ resource: string }> }) {
  const { resource: slug } = await params;
  const resource = getResource(slug);
  if (!resource) notFound();

  const { options, clientFields } = await loadFormOptions(resource);
  const action = createResource.bind(null, resource.slug);

  // Calisan modunda hayvan girisi cift onaylidir: once "Incele ve Onayla"
  // ile ozet gosterilir, kayit ancak ikinci onaydan sonra olusturulur ve
  // bu andan itibaren Calisan icin kilitlenir (bkz. app/modules/animal).
  const me = await apiGet<MeResponse>('/auth/me');
  const requireConfirmation = slug === 'animals' && me.role === 'CALISAN';

  // Bir asim (tohumlama) kaydi girilirken, secilen "Anne Adayi" o an
  // zaten "Gebe" olarak kayitliysa formu engellemeden bir uyari gosterir
  // - sistem sebebi (dusuk mu, yanlis giris mi) varsaymaz, sadece
  // celiskiyi gorunur kilar (bkz. reports.list_pregnant_animals).
  const warningField =
    slug === 'breeding-events'
      ? {
          fieldName: 'dam_id',
          matchValues: (await apiGetSafe<ApiRecord[]>('/reports/pregnant-animals', [])).map((a) =>
            String(a.animal_id)
          ),
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
      {requireConfirmation && (
        <p className="mb-4 max-w-xl rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
          Bu kayıt, onayladıktan sonra sizin tarafınızdan değiştirilemez veya silinemez. Bilgileri dikkatle girin.
        </p>
      )}
      <ResourceForm
        fields={clientFields}
        options={options}
        action={action}
        submitLabel={`${resource.singularTitle} Ekle`}
        requireConfirmation={requireConfirmation}
        warningField={warningField}
      />
    </div>
  );
}
