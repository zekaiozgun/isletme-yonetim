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
