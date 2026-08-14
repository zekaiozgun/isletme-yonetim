/**
 * API'den gelen ISO tarihi (YYYY-MM-DD) DD/MM/YYYY olarak gösterir - tüm
 * uygulamada (raporlar, liste tabloları, çift onay ekranı) tek tarih
 * format kaynağı. Veri girişindeki native <input type="date"> takvim
 * pop-up'ının kendi görünümü tarayıcı/işletim sistemi tarafından
 * kontrol edilir, bu fonksiyonla değiştirilemez.
 */
export function formatDateDMY(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  const [year, month, day] = String(value).split('-');
  if (!year || !month || !day) return String(value);
  return `${day}/${month}/${year}`;
}

/**
 * Bir sayıyı Türkçe noktalama kuralıyla (binlik ayırıcı nokta, ondalık
 * ayırıcı virgül - örn. 1.234,5) gösterir - para birimi, ağırlık (kg) gibi
 * birim eki gerektirmeyen HER ondalık değer için ortak kaynak. API'den
 * gelen ham değer her zaman nokta ondalıklı bir sayı/string'tir (örn.
 * 1234.5), bu fonksiyon olmadan doğrudan gösterilirse binlik ayırıcı hiç
 * olmaz ve virgül yerine nokta görünür. Tam sayılarda gereksiz ",00"
 * eklemez (maximumFractionDigits var, minimumFractionDigits yok).
 */
export function formatNumberTR(value: unknown, maxFractionDigits = 2): string {
  if (value === null || value === undefined || value === '') return '—';
  const num = Number(value);
  if (Number.isNaN(num)) return String(value);
  return num.toLocaleString('tr-TR', { maximumFractionDigits: maxFractionDigits });
}

/**
 * Bir parasal değeri Türkçe noktalama kuralıyla (binlik ayırıcı nokta,
 * ondalık ayırıcı virgül - örn. 1.234,56) gösterir - tüm uygulamada
 * (rapor sütunları, kaynak liste tabloları) tek para birimi format
 * kaynağı. Para birimlerinde kuruş/sent her zaman iki hane gösterilir
 * (formatNumberTR'nin aksine minimumFractionDigits de sabit 2).
 */
export function formatCurrencyTRY(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  const num = Number(value);
  if (Number.isNaN(num)) return String(value);
  return `${num.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₺`;
}

/** formatCurrencyTRY ile aynı noktalama kuralı, USD için (₺ yerine $ önekiyle). */
export function formatUsdValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  const num = Number(value);
  if (Number.isNaN(num)) return String(value);
  return `$${num.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

const AGE_DAY_DISPLAY_THRESHOLD_DAYS = 60;

/**
 * Ay bazlı yaş küçük hayvanlarda (buzağı) her zaman tam sayıya
 * yuvarlandığından gün/ay küsuratı görünmüyordu - 2 günlük bir buzağı ile
 * 29 günlük bir buzağı ekranda ikisi de "0 ay" görünüyordu (bkz. kullanıcı
 * geri bildirimi). Eşiğin altında (60 gün) gerçek gün sayısını, üstünde
 * mevcut ay değerini gösterir - olgun hayvanların görünümü değişmez.
 */
function formatAgeFromDaysAndMonths(days: unknown, months: unknown): string {
  if (typeof days === 'number' && days < AGE_DAY_DISPLAY_THRESHOLD_DAYS) {
    return `${days} gün`;
  }
  if (typeof months === 'number') return `${months} ay`;
  return '—';
}

/** age_days alanı taşıyan satırlar için (bkz. YoungAnimalRead, AnimalRead, AnimalMarketValueRead). */
export function formatAgeMixed(value: unknown, row: Record<string, unknown>): string {
  return formatAgeFromDaysAndMonths(row.age_days, value);
}

/** exit_age_days alanı taşıyan satırlar için (bkz. HerdExitRead - Sürüden Çıkış Raporu). */
export function formatExitAgeMixed(value: unknown, row: Record<string, unknown>): string {
  return formatAgeFromDaysAndMonths(row.exit_age_days, value);
}

/**
 * "Şimdi"yi DD/MM/YYYY HH:MM olarak, sunucunun kendi saat dilimi ne olursa
 * olsun (Render'da genelde UTC) her zaman Türkiye yerel saatiyle gösterir -
 * rapor sayfaları bu Server Component'te render edildiği anı damgalar,
 * böylece daha sonra "bu rapor ne zaman alınmıştı" diye bakılabilir.
 */
export function formatNowIstanbulDMYHM(): string {
  const parts = new Intl.DateTimeFormat('tr-TR', {
    timeZone: 'Europe/Istanbul',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(new Date());
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? '';
  return `${get('day')}/${get('month')}/${get('year')} ${get('hour')}:${get('minute')}`;
}
