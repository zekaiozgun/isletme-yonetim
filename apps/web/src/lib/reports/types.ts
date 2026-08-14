import type { ApiRecord } from '../api';

export interface ReportColumn {
  key: string;
  label: string;
  format?: (value: unknown, row: ApiRecord) => string;
  /** Sütun genişlik sınıfı - A4 baskıya uygun mizanpaj için:
   * 'narrow' = kısa değerler (tarih, yaş, sayı, kod) - başta/sonda 1
   *   karakterlik dolgu ile sıkışıklık hissi vermeden dar tutulur.
   * 'wide' = serbest metin (not, açıklama) - daha geniş ama TEK SATIR
   *   kalır, taşarsa "…" ile kesilir (üzerine gelince tam metin görünür).
   * Belirtilmezse normal (varsayılan) genişlik kullanılır. */
  width?: 'narrow' | 'wide';
  /** Belirtilirse, bu satır için hücrenin metin rengi/kalınlığı bu sınıfla
   * DEĞİŞTİRİLİR (satır vurgusunun rengiyle birleştirilmez) - örn. bir
   * uyarı hücresini kırmızı göstermek için. format()'ın döndürdüğü METNİ
   * etkilemez, CSV/PDF export'u bundan etkilenmez. */
  cellClassName?: (row: ApiRecord) => string;
}

export interface ReportConfig {
  slug: string;
  title: string;
  description: string;
  /** Raporlar hub sayfasında (`/reports`) kartları konuya göre bölümlere
   * ayırmak için kullanılır - bkz. `groupedDateRangeReports()`. */
  group: string;
  endpoint: string;
  columns: ReportColumn[];
  /** true dönerse satır dikkat çekecek şekilde vurgulanır (örn. gecikmiş gebelik kontrolü). */
  rowHighlight?: (row: ApiRecord) => boolean;
  /** true ise rapor sayfası bir başlangıç/bitiş tarihi filtresi gösterir ve
   * bunları `start_date`/`end_date` query param'ı olarak endpoint'e ekler. */
  dateRange?: boolean;
  /** Belirtilirse, hiçbir tarih seçilmeden ilk açıldığında başlangıç
   * tarihi bugünden bu kadar gün öncesi olur (örn. 365 = 1 yıl önce) -
   * belirtilmezse varsayılan "bu ayın başı" kullanılır. Kullanıcı her
   * zaman kendi tarih aralığını seçip bunu değiştirebilir. */
  defaultRangeDays?: number;
  /** true ise rapor sayfası tek bir "tarih itibariyle" filtresi gösterir
   * (aralık değil) ve bunu `as_of_date` query param'ı olarak endpoint'e ekler. */
  singleDate?: boolean;
  /** true ise rapor sayfası hayvan statüsü (Aktif/Satıldı/Öldü vb.) için
   * çoklu seçim checkbox filtresi gösterir; hiçbiri seçilmemiş ve form hiç
   * gönderilmemişse varsayılan olarak "Aktif" seçili gelir. Seçilenler
   * `status_ids` query param'ı olarak (tekrarlı) endpoint'e eklenir. */
  statusFilter?: boolean;
  /** true ise rapor sayfasının üstünde Büyüme Değerleme Çıpalarını
   * düzenleme sayfasına giden bir link gösterilir (bu rapor o verilere
   * dayandığı için). */
  usesGrowthCheckpoints?: boolean;
  /** Belirtilirse, rapor sayfasının üstünde açılabilir ("Bu rapor nasıl
   * çalışır?") bir açıklama metni gösterilir - raporun altındaki mantığı
   * (örn. doğum sonrası bekleme süresi gibi anlık görünmeyebilecek
   * kuralları) kullanıcıya açık şekilde anlatmak için. */
  helpNote?: string;
  /** Belirtilirse, tablonun üstünde bu sütuna göre gruplanmış kayıt
   * sayısı özeti gösterilir (örn. "Toplam: 45 · Aktif: 40 · Öldü: 3 · Satıldı: 2").
   * Sütunun kendi label'ı grup adı olarak kullanılır. */
  groupSummaryKey?: string;
  /** true ise arama TÜM satırları önceden indirip istemcide gizlemek
   * (varsayılan davranış) yerine SUNUCU TARAFINDA yapılır: kutuya yazıp
   * Enter'a basmak `q` query param'ıyla sayfayı yeniden yükler, backend
   * SADECE eşleşen satırları döner. Zamanla sınırsız büyüyebilecek (soy
   * kaydı gibi asla küçülmeyen) raporlar için kullanılır - bkz.
   * apps/api'deki ilgili list_* fonksiyonunun `q` parametresi. */
  serverSearch?: boolean;
  /** Belirtilirse ReportTable yerine GroupedOffspringList kullanılır: satırlar
   * key()'e göre gruplanır, her grup büyük punto bir üst başlık (label()) +
   * altında sıra numaralı bir alt tablo (columns) olarak gösterilir - örn.
   * Anne/Baba Bazında Yavru Listesi. Gruplar, satırların sunucudan geldiği
   * sırayla (ilk görülme) listelenir. */
  groupBy?: {
    key: (row: ApiRecord) => string;
    label: (row: ApiRecord) => string;
  };
}
