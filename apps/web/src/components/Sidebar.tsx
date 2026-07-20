import Link from 'next/link';
import { groupedResources } from '@/lib/resources';

export function Sidebar() {
  const groups = groupedResources();

  return (
    <nav className="w-64 shrink-0 border-r border-slate-200 bg-slate-50 p-4">
      <Link href="/" className="mb-6 block text-lg font-semibold text-slate-900">
        İşletme Yönetim
      </Link>
      <ul className="space-y-5">
        {groups.map((group) => (
          <li key={group.group}>
            <div className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
              {group.group}
            </div>
            <ul className="space-y-0.5">
              {group.items.map((resource) => (
                <li key={resource.slug}>
                  <Link
                    href={`/${resource.slug}`}
                    className="block rounded px-2 py-1.5 text-sm text-slate-700 hover:bg-slate-200"
                  >
                    {resource.title}
                  </Link>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </nav>
  );
}
