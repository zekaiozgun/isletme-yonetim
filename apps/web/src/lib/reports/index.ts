import type { ReportConfig } from './types';
import { breedingReports } from './breeding';
import { healthReports } from './health';
import { growthReports } from './growth';
import { outcomeReports } from './outcomes';
import { herdReports } from './herd';
import { pensFeedReports } from './pens-feed';
import { financialReports } from './financial';

export type { ReportColumn, ReportConfig } from './types';
export { formatMonths, formatSireIdentity, formatSourceCode } from './formatters';

/** Tüm raporların tek listesi - mantıksal gruplara bölünmüş dosyalardan
 * (breeding/health/growth/outcomes/herd/pens-feed/financial) birleştirilir.
 * Sıra, orijinal (bölünmeden önceki) sırayla aynıdır. */
export const reports: ReportConfig[] = [
  ...breedingReports,
  ...healthReports,
  ...growthReports,
  ...outcomeReports,
  ...herdReports,
  ...pensFeedReports,
  ...financialReports,
];

export function getReport(slug: string): ReportConfig | undefined {
  return reports.find((r) => r.slug === slug);
}

/** /reports hub sayfasında listelenen (filtreli) raporlar - reports[]'ten türetilir. */
export function dateRangeReports(): ReportConfig[] {
  return reports.filter((r) => r.dateRange || r.singleDate || r.statusFilter);
}
