import Link from 'next/link';

const statusDot: Record<'neutral' | 'warning' | 'critical', string> = {
  neutral: 'bg-slate-300',
  warning: 'bg-amber-500',
  critical: 'bg-red-500',
};

const statusBorder: Record<'neutral' | 'warning' | 'critical', string> = {
  neutral: 'border-slate-200',
  warning: 'border-amber-200',
  critical: 'border-red-200',
};

export function StatTile({
  label,
  value,
  href,
  status = 'neutral',
}: {
  label: string;
  value: string;
  href: string;
  status?: 'neutral' | 'warning' | 'critical';
}) {
  return (
    <Link
      href={href}
      className={`block rounded border ${statusBorder[status]} bg-white p-4 transition hover:shadow-sm`}
    >
      <div className="mb-1.5 flex items-center gap-1.5">
        <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${statusDot[status]}`} aria-hidden />
        <span className="text-xs font-medium text-slate-500">{label}</span>
      </div>
      <div className="text-2xl font-semibold text-slate-900">{value}</div>
    </Link>
  );
}
