import type { ApiRecord } from '../api';
import { formatDateDMY as formatDate, formatCurrencyTRY, formatUsdValue, formatNumberTR } from '../format';

export { formatDate };

export function formatDays(value: unknown): string {
  if (value === null || value === undefined) return '—';
  return `${String(value)} gün`;
}

/** Birim artık sütun başlığında ("Yaş (ay)") olduğu için hücre sadece
 * sayıyı gösterir. */
export function formatMonths(value: unknown): string {
  if (value === null || value === undefined) return '—';
  return String(value);
}

export function formatGenderShort(value: unknown): string {
  if (value === 'Dişi') return 'D';
  if (value === 'Erkek') return 'E';
  return '—';
}

export function formatPercent(value: unknown): string {
  if (value === null || value === undefined) return '—';
  return `%${String(value)}`;
}

export function formatPlain(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  return String(value);
}

export function formatKg(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  return `${formatNumberTR(value)} kg`;
}

export function formatReturnedFromPregnancy(value: unknown): string {
  return value === true ? '⚠ Önceden Gebeydi' : '—';
}

export function formatDaysUntilCalving(value: unknown): string {
  if (typeof value !== 'number') return '—';
  if (value < 0) return 'Gecikti';
  if (value === 0) return 'Bugün';
  return `${value} gün`;
}

/** Tohumlu ve Gebe Hayvanlar raporunda ayrı bir "Uyarı" sütunu yerine,
 * dikkat gerektiren satırlarda (kontrol zamanı gelmiş ya da önceden
 * gebeydi çelişkisi var) doğrudan Durum hücresini kırmızı/kalın gösterir
 * - satır zaten amber vurgulu olduğundan ayrı bir metin sütunu
 * gerekmiyor, bu tek başına yeterince göze batıyor. */
export function bredAnimalStatusClass(row: ApiRecord): string {
  const needsAttention = row.pregnancy_check_due === true || row.returned_from_pregnancy === true;
  return needsAttention ? 'font-bold text-red-600' : 'text-slate-700';
}

/** Anne (value) ve Baba (row.father_sire_name) küpe/isim bilgisini tek
 * sütunda "anne / baba" olarak gösterir - iki ayrı sütuna göre hem yer
 * kazandırır hem de eksik tarafı ("1234 / —") tek bakışta fark ettirir. */
export function formatParentage(value: unknown, row: ApiRecord): string {
  const mother = typeof value === 'string' && value ? value : null;
  const father = typeof row.father_sire_name === 'string' && row.father_sire_name ? row.father_sire_name : null;
  if (!mother && !father) return '—';
  return `${mother ?? '—'} / ${father ?? '—'}`;
}

/** Baba Bazında Yavru Listesi raporunda boğa kimliğini gösterir - öncelik
 * sırası: küpe no (sürüye ait bir boğaysa) -> soy kütüğü kayıt no (dış
 * kaynaklı boğalarda girilmiş olabilir) -> hiçbiri yoksa sistemin kendi
 * iç kayıt no'su (sire_id). Hiçbiri uydurma değildir, zaten var olan bir
 * facttir - sadece hangisinin gösterileceği değişir (bkz. backend
 * OffspringBySireRead). Her durumda boğa adıyla birlikte gösterilir.
 */
export function formatSireIdentity(value: unknown, row: ApiRecord): string {
  const name = typeof row.sire_name === 'string' && row.sire_name ? row.sire_name : '—';
  if (typeof row.sire_tag_number === 'string' && row.sire_tag_number) {
    return `${row.sire_tag_number} — ${name}`;
  }
  if (typeof row.sire_registry_no === 'string' && row.sire_registry_no) {
    return `Kayıt No ${row.sire_registry_no} — ${name}`;
  }
  return `Kayıt No ${String(value)} — ${name}`;
}

export function formatDosage(value: unknown, row: ApiRecord): string {
  if (value === null || value === undefined || value === '') return '—';
  const unit = row.dosage_unit_name;
  return unit ? `${String(value)} ${String(unit)}` : String(value);
}

export function formatKgPerDay(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  return `${formatNumberTR(value, 3)} kg/gün`;
}

export const formatCurrency = formatCurrencyTRY;

export const formatUsd = formatUsdValue;

/** Sürü Durum Özeti raporunda "Doğurgan Yaştaki Dişi" altındaki üreme
 * alt-durumu satırlarını (level=1) girintiyle gösterir - bu satırların
 * toplamı üstteki ara toplama tam eşit olduğu için görsel olarak da
 * o satıra bağlı bir kırılım gibi okunsun diye. */
export function formatHerdStatusCategory(value: unknown, row: ApiRecord): string {
  const label = typeof value === 'string' ? value : '—';
  return row.level === 1 ? `— ${label}` : label;
}

export function herdStatusRowClass(row: ApiRecord): string {
  return row.is_total === true ? 'font-semibold text-slate-900' : 'text-slate-700';
}

export function formatSourceCode(value: unknown): string {
  if (value === 'market_estimate') return 'Piyasa Tahmini';
  if (value === 'cost_basis') return 'Maliyet Bazlı';
  if (value === 'mixed') return 'Karışık';
  return '—';
}
