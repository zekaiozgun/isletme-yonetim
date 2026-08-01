import { groupedDateRangeReports } from '@/lib/reports';
import Link from 'next/link';

export default function ReportsHubPage() {
  const groups = groupedDateRangeReports();

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Raporlar</h1>
      <p className="mb-6 text-sm text-slate-500">İki tarih arasında filtrelenebilecek genel raporlar.</p>

      <div className="space-y-8">
        {groups.map((group) => (
          <div key={group.group}>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">{group.group}</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {group.items.map((report) => (
                <Link
                  key={report.slug}
                  href={`/reports/${report.slug}`}
                  className="block rounded border border-slate-200 p-4 transition hover:border-slate-300 hover:shadow-sm"
                >
                  <h3 className="mb-1 text-sm font-semibold text-slate-900">{report.title}</h3>
                  <p className="text-sm text-slate-500">{report.description}</p>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
