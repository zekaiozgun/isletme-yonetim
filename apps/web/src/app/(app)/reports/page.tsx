import { generalReportPlans } from '@/lib/reports';
import Link from 'next/link';

export default function ReportsHubPage() {
  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">Raporlar</h1>
      <p className="mb-6 text-sm text-slate-500">İki tarih arasında filtrelenebilecek genel raporlar.</p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {generalReportPlans.map((report) =>
          report.slug ? (
            <Link
              key={report.title}
              href={`/reports/${report.slug}`}
              className="block rounded border border-slate-200 p-4 transition hover:border-slate-300 hover:shadow-sm"
            >
              <h2 className="mb-1 text-sm font-semibold text-slate-900">{report.title}</h2>
              <p className="text-sm text-slate-500">{report.description}</p>
            </Link>
          ) : (
            <div key={report.title} className="rounded border border-slate-200 bg-slate-50 p-4 opacity-70">
              <div className="mb-1 flex items-center gap-2">
                <h2 className="text-sm font-semibold text-slate-700">{report.title}</h2>
                <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-500">Yakında</span>
              </div>
              <p className="text-sm text-slate-500">{report.description}</p>
            </div>
          )
        )}
      </div>
    </div>
  );
}
