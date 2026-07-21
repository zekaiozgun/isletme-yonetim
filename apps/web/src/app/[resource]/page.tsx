import Link from 'next/link';
import { notFound } from 'next/navigation';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { getResource } from '@/lib/resources';
import { ResourceTable } from '@/components/ResourceTable';

export default async function ResourceListPage({ params }: { params: Promise<{ resource: string }> }) {
  const { resource: slug } = await params;
  const resource = getResource(slug);
  if (!resource) notFound();

  // include_inactive=true: bu kaynagin kendi liste sayfasinda pasif
  // (is_active=false) lookup kayitlari da gorunur olmali ki yonetilebilsin;
  // diger formlardaki secim listeleri (OptionSource) bu parametreyi
  // GONDERMEZ, o yuzden orada hala sadece aktif kayitlar teklif edilir.
  const separator = resource.listEndpoint.includes('?') ? '&' : '?';
  const rows = await apiGetSafe<ApiRecord[]>(`${resource.listEndpoint}${separator}include_inactive=true`, []);

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900">{resource.title}</h1>
        <Link
          href={`/${resource.slug}/new`}
          className="rounded bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700"
        >
          + Yeni {resource.singularTitle}
        </Link>
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
      <ResourceTable resource={resource} rows={rows} />
    </div>
  );
}
