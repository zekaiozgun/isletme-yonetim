import { notFound } from 'next/navigation';
import { apiGetSafe, type ApiRecord } from '@/lib/api';
import { getReport } from '@/lib/reports';
import { ReportTable } from '@/components/ReportTable';

export default async function ReportPage({ params }: { params: Promise<{ report: string }> }) {
  const { report: slug } = await params;
  const report = getReport(slug);
  if (!report) notFound();

  const rows = await apiGetSafe<ApiRecord[]>(report.endpoint, []);

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">{report.title}</h1>
      <p className="mb-4 text-sm text-slate-500">{report.description}</p>
      <ReportTable report={report} rows={rows} />
    </div>
  );
}
