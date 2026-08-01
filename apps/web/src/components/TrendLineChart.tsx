import { formatDateDMY } from '@/lib/format';

export interface TrendPoint {
  date: string;
  value: number;
}

const WIDTH = 600;
const HEIGHT = 170;
const MARGIN_TOP = 24;
const MARGIN_BOTTOM = 20;
const MARGIN_X = 24;

/**
 * Sunucuda render edilen, JS gerektirmeyen basit bir SVG çizgi grafiği -
 * tarih eksenine göre orantılı konumlandırma (ölçümler eşit aralıklı
 * olmayabilir, bkz. WeightRecord). Her noktanın değeri DOĞRUDAN grafik
 * üzerinde yazılı gösterilir (mobil/dokunmatik cihazlarda hover
 * çalışmadığı için sadece tooltip'e güvenilemez) - <title> tooltip'i
 * ayrıca tarihi de vermek için tutuluyor. Zaman serisi görselleştirme
 * önerileri listesindeki diğer maddeler (aylık maliyet, kayıp oranı vb.)
 * için de aynı şekilde tekrar kullanılabilir.
 */
export function TrendLineChart({
  points,
  unit = '',
  color = '#0f172a',
}: {
  points: TrendPoint[];
  unit?: string;
  color?: string;
}) {
  if (points.length < 2) return null;

  const dateMs = points.map((p) => new Date(p.date).getTime());
  const minDateMs = Math.min(...dateMs);
  const maxDateMs = Math.max(...dateMs);
  const dateSpan = maxDateMs - minDateMs || 1;

  const values = points.map((p) => p.value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const valuePadding = (maxValue - minValue) * 0.2 || Math.abs(maxValue) * 0.1 || 1;
  const yMin = minValue - valuePadding;
  const yMax = maxValue + valuePadding;
  const ySpan = yMax - yMin || 1;

  const plotWidth = WIDTH - MARGIN_X * 2;
  const plotHeight = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM;

  function xFor(ms: number): number {
    return MARGIN_X + ((ms - minDateMs) / dateSpan) * plotWidth;
  }
  function yFor(value: number): number {
    return MARGIN_TOP + plotHeight - ((value - yMin) / ySpan) * plotHeight;
  }

  const pathD = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${xFor(new Date(p.date).getTime()).toFixed(1)} ${yFor(p.value).toFixed(1)}`)
    .join(' ');

  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full" role="img" aria-label="Trend grafiği">
      <line
        x1={MARGIN_X}
        y1={MARGIN_TOP + plotHeight}
        x2={WIDTH - MARGIN_X}
        y2={MARGIN_TOP + plotHeight}
        stroke="#e2e8f0"
        strokeWidth={1}
      />
      <path d={pathD} fill="none" stroke={color} strokeWidth={2} />
      {points.map((p, i) => {
        const cx = xFor(new Date(p.date).getTime());
        const cy = yFor(p.value);
        const isFirst = i === 0;
        const isLast = i === points.length - 1;
        const anchor: 'start' | 'end' | 'middle' = isFirst ? 'start' : isLast ? 'end' : 'middle';
        // Ust kenara cok yakinsa (deger etiketinin sigacak yeri yoksa)
        // etiketi noktanin ALTINA koy, aksi halde USTUNE (varsayilan).
        const labelAbove = cy - MARGIN_TOP > 12;
        const labelY = labelAbove ? cy - 8 : cy + 15;
        return (
          <g key={i}>
            <circle cx={cx} cy={cy} r={3.5} fill={color}>
              <title>{`${formatDateDMY(p.date)}: ${p.value}${unit ? ' ' + unit : ''}`}</title>
            </circle>
            <text x={cx} y={labelY} fontSize="10" fontWeight={600} fill={color} textAnchor={anchor}>
              {p.value}
            </text>
          </g>
        );
      })}
      <text x={MARGIN_X} y={HEIGHT - 4} fontSize="11" fill="#94a3b8">
        {formatDateDMY(points[0].date)}
      </text>
      <text x={WIDTH - MARGIN_X} y={HEIGHT - 4} fontSize="11" fill="#94a3b8" textAnchor="end">
        {formatDateDMY(points[points.length - 1].date)}
      </text>
    </svg>
  );
}
