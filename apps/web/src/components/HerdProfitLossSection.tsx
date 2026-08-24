import type { ApiRecord } from '@/lib/api';
import { formatCurrencyTRY as formatCurrency, formatUsdValue as formatUsd, formatDateDMY } from '@/lib/format';

type Tone = 'nakit' | 'maliyet' | 'piyasa';

function ValueTag({ tone }: { tone: Tone }) {
  const label = tone === 'nakit' ? 'Nakit' : tone === 'maliyet' ? 'Maliyet' : 'Piyasa';
  const toneClass =
    tone === 'nakit'
      ? 'bg-slate-200 text-slate-600'
      : tone === 'maliyet'
        ? 'bg-amber-100 text-amber-800'
        : 'bg-blue-100 text-blue-800';
  return <span className={`whitespace-nowrap rounded-full px-2 py-0.5 text-[10px] font-medium ${toneClass}`}>{label}</span>;
}

function signedAmountClass(amount: number): string {
  if (amount < 0) return 'text-red-600';
  if (amount > 0) return 'text-emerald-700';
  return 'text-slate-900';
}

function EcoRow({ label, usdAmount, tone }: { label: string; usdAmount: number; tone: Tone }) {
  return (
    <div className="flex items-center justify-between px-4 py-2.5">
      <span className="text-sm text-slate-600">{label}</span>
      <span className="flex items-center gap-2">
        <ValueTag tone={tone} />
        <span className={`min-w-[90px] text-right text-sm font-semibold ${signedAmountClass(usdAmount)}`}>
          {usdAmount > 0 ? '+' : ''}
          {formatUsd(usdAmount)}
        </span>
      </span>
    </div>
  );
}

function BridgeRow({ label, tryAmount, usdAmount, sub }: { label: string; tryAmount: number; usdAmount: number; sub?: React.ReactNode }) {
  return (
    <div className="border-b border-slate-100 px-3 py-2 last:border-b-0">
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500">{label}</span>
        <span className={`text-xs font-semibold ${signedAmountClass(usdAmount)}`}>
          {usdAmount > 0 ? '+' : ''}
          {formatUsd(usdAmount)}
        </span>
      </div>
      {sub}
      <p className="mt-0.5 text-[11px] text-slate-400">{formatCurrency(tryAmount)}</p>
    </div>
  );
}

/** Sürü Kâr/Zarar Raporu: Ekonomik Sonuç üstte tek vurgulu satır (Net
 * Ekonomik Kâr/Zarar), altında Piyasa Değer Köprüsü açılır bir detay -
 * biri diğerinin İÇİNDEKİ tek bir satırın (value_bridge_net_*) dökümü,
 * eşit ağırlıkta iki ayrı rapor değil (bkz. reports/service.py
 * get_herd_profit_loss docstring'i, tam mantık için). */
export function HerdProfitLossSection({ data }: { data: ApiRecord }) {
  const num = (key: string) => Number(data[key] ?? 0);

  const netTry = num('net_result_try');
  const netUsd = num('net_result_usd');
  const netTone = netUsd < 0 ? { bg: 'bg-red-50', text: 'text-red-900', amount: 'text-red-600' } : { bg: 'bg-emerald-50', text: 'text-emerald-900', amount: 'text-emerald-700' };

  const birthsCostUsd = num('births_cost_usd');
  const birthsProfitUsd = num('births_profit_usd');

  return (
    <div className="max-w-2xl overflow-hidden rounded border border-slate-300 bg-slate-100">
      <div className="border-b border-slate-300 bg-slate-200 px-4 py-2.5">
        <p className="text-sm font-semibold text-slate-700">
          Dönem Ekonomik Sonucu · {formatDateDMY(String(data.start_date))} → {formatDateDMY(String(data.end_date))}
        </p>
      </div>

      <div className="divide-y divide-slate-200">
        <EcoRow label="Satış Geliri" usdAmount={num('sale_revenue_usd')} tone="nakit" />
        <EcoRow label="Satın Alma Bedeli" usdAmount={-num('purchase_cost_usd')} tone="nakit" />
        <EcoRow label="Yem Maliyeti" usdAmount={-num('feed_cost_usd')} tone="maliyet" />
        <EcoRow label="Sağlık/Tedavi Maliyeti" usdAmount={-num('health_cost_usd')} tone="maliyet" />

        <details className="px-4 py-2.5">
          <summary className="flex cursor-pointer list-none items-center justify-between text-sm">
            <span className="flex items-center gap-1.5 text-slate-600">
              Piyasa Değer Köprüsü Net Değişimi
              <span className="text-slate-400">▾</span>
            </span>
            <span className="flex items-center gap-2">
              <ValueTag tone="piyasa" />
              <span className={`min-w-[90px] text-right text-sm font-semibold ${signedAmountClass(num('value_bridge_net_usd'))}`}>
                {num('value_bridge_net_usd') > 0 ? '+' : ''}
                {formatUsd(num('value_bridge_net_usd'))}
              </span>
            </span>
          </summary>

          <div className="mt-2 rounded border border-slate-300 bg-white">
            <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2">
              <span className="text-xs text-slate-500">Dönem Başı Piyasa Değeri</span>
              <span className="text-xs font-semibold text-slate-900">{formatUsd(num('opening_value_usd'))}</span>
            </div>

            <BridgeRow
              label="+ Doğumla Giren Değer"
              tryAmount={num('births_value_try')}
              usdAmount={num('births_value_usd')}
              sub={
                num('births_count') > 0 ? (
                  <div className="mt-1 flex flex-wrap gap-x-3 gap-y-0.5 pl-1">
                    <span className="text-[11px] text-slate-400">{data.births_count as number} buzağı</span>
                    <span className="text-[11px] text-slate-400">Maliyet (anne yem payı): {formatUsd(birthsCostUsd)}</span>
                    <span className="text-[11px] text-slate-400">Doğum Kârı: {formatUsd(birthsProfitUsd)}</span>
                  </div>
                ) : undefined
              }
            />
            <BridgeRow label="+ Satın Alımla Giren Değer" tryAmount={num('purchases_value_try')} usdAmount={num('purchases_value_usd')} />
            <BridgeRow label="± Mevcut Sürünün Değer Değişimi" tryAmount={num('revaluation_try')} usdAmount={num('revaluation_usd')} />
            <BridgeRow label="− Ölüm Kaybı" tryAmount={-num('death_loss_try')} usdAmount={-num('death_loss_usd')} />
            <BridgeRow label="− Satılan Hayvanların Piyasa Değeri" tryAmount={-num('sold_value_try')} usdAmount={-num('sold_value_usd')} />

            <div className="flex items-center justify-between bg-slate-50 px-3 py-2">
              <span className="text-xs font-semibold text-slate-700">Dönem Sonu Piyasa Değeri</span>
              <span className="text-xs font-bold text-slate-900">{formatUsd(num('closing_value_usd'))}</span>
            </div>
          </div>
        </details>
      </div>

      <div className={`flex items-center justify-between px-4 py-3 ${netTone.bg}`}>
        <span className={`text-sm font-semibold ${netTone.text}`}>Net Ekonomik Kâr/Zarar</span>
        <div className="text-right">
          <span className={`text-base font-bold ${netTone.amount}`}>
            {netUsd > 0 ? '+' : ''}
            {formatUsd(netUsd)}
          </span>
          <p className="text-xs text-slate-400">{formatCurrency(netTry)}</p>
        </div>
      </div>
    </div>
  );
}
