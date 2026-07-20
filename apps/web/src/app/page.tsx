import Link from 'next/link';
import { groupedResources } from '@/lib/resources';

export default function Home() {
  const groups = groupedResources();

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold text-slate-900">İşletme Yönetim</h1>
      <p className="mb-6 text-slate-500">Bir modül seçerek kayıtları görüntüleyin veya yeni kayıt ekleyin.</p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((group) => (
          <div key={group.group} className="rounded border border-slate-200 p-4">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">{group.group}</h2>
            <ul className="space-y-1">
              {group.items.map((resource) => (
                <li key={resource.slug}>
                  <Link href={`/${resource.slug}`} className="text-sm text-slate-700 hover:text-slate-900 hover:underline">
                    {resource.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
