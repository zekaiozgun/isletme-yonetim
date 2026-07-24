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
