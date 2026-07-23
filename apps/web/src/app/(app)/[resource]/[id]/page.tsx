import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGet, apiGetSafe, type ApiRecord } from '@/lib/api';
import { deleteResource, updateResource } from '@/lib/actions';
import { loadFormOptions } from '@/lib/formOptions';
import { getResource } from '@/lib/resources';
import { ResourceForm } from '@/components/ResourceForm';
import { DeleteButton } from '@/components/DeleteButton';

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

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href={`/${resource.slug}`} className="text-sm text-slate-500 hover:text-slate-800">
          ← {resource.title}
        </Link>
      </div>
      <h1 className="mb-4 text-xl font-semibold text-slate-900">{resource.singularTitle} Düzenle</h1>
      <ResourceForm
        fields={clientFields}
        options={options}
        action={updateAction}
        submitLabel="Kaydet"
        initialValues={record}
      />

      {canDeleteResource(resource.slug, me.role) ? (
        <div className="mt-8 max-w-xl border-t border-slate-200 pt-6">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Tehlikeli Bölge</h2>
          <p className="mb-3 text-sm text-slate-500">
            Bu {resource.singularTitle.toLowerCase()} kaydını kalıcı olarak siler. Başka kayıtlarca kullanılıyorsa
            silme işlemi engellenir.
          </p>
          <DeleteButton action={deleteAction} confirmMessage={`Bu ${resource.singularTitle.toLowerCase()} kaydını silmek istediğinize emin misiniz?`} />
        </div>
      ) : (
        <p className="mt-8 max-w-xl border-t border-slate-200 pt-6 text-sm text-slate-400">
          Hayvan kayıtlarını silme yetkisi yalnızca yöneticilerdedir.
        </p>
      )}
    </div>
  );
}
