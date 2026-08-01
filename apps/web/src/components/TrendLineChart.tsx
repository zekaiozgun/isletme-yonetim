import { formatDateDMY } from '@/lib/format';

export interface TrendPoint {
  date: string;
  value: number;
}

const WIDTH = 600;
const HEIGHT = 160;
const MARGIN_TOP = 18;
const MARGIN_BOTTOM = 20;
const MARGIN_X = 4;

/**
 * Sunucuda render edilen, JS gerektirmeyen basit bir SVG çizgi grafiği -
 * tarih eksenine göre orantılı konumlandırma (ölçümler eşit aralıklı
 * olmayabilir, bkz. WeightRecord). Nokta üzerine gelince tarayıcının
 * yerleşik <title> tooltip'i tam değeri gösterir - ayrı bir client
 * bileşeni/kütüphane gerekmez. Zaman serisi görselleştirme önerileri
 * listesindeki diğer maddeler (aylık maliyet, kayıp oranı vb.) için de
 * aynı şekilde tekrar kullanılabilir.
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
  const valuePadding = (maxValue - minValue) * 0.1 || Math.abs(maxValue) * 0.1 || 1;
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
      {points.map((p, i) => (
        <circle key={i} cx={xFor(new Date(p.date).getTime())} cy={yFor(p.value)} r={3.5} fill={color}>
          <title>{`${formatDateDMY(p.date)}: ${p.value}${unit ? ' ' + unit : ''}`}</title>
        </circle>
      ))}
      <text x={MARGIN_X} y={12} fontSize="11" fill="#64748b">
        {`${Math.round(yMax * 10) / 10}${unit ? ' ' + unit : ''}`}
      </text>
      <text x={MARGIN_X} y={HEIGHT - 4} fontSize="11" fill="#94a3b8">
        {formatDateDMY(points[0].date)}
      </text>
      <text x={WIDTH - MARGIN_X} y={HEIGHT - 4} fontSize="11" fill="#94a3b8" textAnchor="end">
        {formatDateDMY(points[points.length - 1].date)}
      </text>
    </svg>
  );
}
