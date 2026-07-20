import Link from 'next/link';
import { notFound } from 'next/navigation';
import { createResource } from '@/lib/actions';
import { loadFormOptions } from '@/lib/formOptions';
import { getResource } from '@/lib/resources';
import { ResourceForm } from '@/components/ResourceForm';

export default async function NewResourcePage({ params }: { params: Promise<{ resource: string }> }) {
  const { resource: slug } = await params;
  const resource = getResource(slug);
  if (!resource) notFound();

  const { options, clientFields } = await loadFormOptions(resource);
  const action = createResource.bind(null, resource.slug);

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <Link href={`/${resource.slug}`} className="text-sm text-slate-500 hover:text-slate-800">
          ← {resource.title}
        </Link>
      </div>
      <h1 className="mb-4 text-xl font-semibold text-slate-900">Yeni {resource.singularTitle}</h1>
      <ResourceForm
        fields={clientFields}
        options={options}
        action={action}
        submitLabel={`${resource.singularTitle} Ekle`}
      />
    </div>
  );
}
