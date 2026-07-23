import type { ApiRecord } from './api';

export type FieldType = 'text' | 'number' | 'decimal' | 'date' | 'select' | 'checkbox' | 'textarea' | 'password';

/** Bir <select> alanını doldurmak için API'den çekilecek liste (lookup ya da başka bir kaynağın kayıtları). */
export interface OptionSource {
  endpoint: string;
  label: (item: ApiRecord) => string;
  value?: (item: ApiRecord) => string;
}

export interface FieldConfig {
  name: string;
  label: string;
  type: FieldType;
  required?: boolean;
  options?: OptionSource;
  defaultValue?: string;
}

export interface ColumnConfig {
  key: string;
  label: string;
  /** Değer bir FK id ise, bu kaynaktan isim çözümlemek için. */
  lookup?: OptionSource;
  /** true ise değer bool olarak "Evet"/"Hayır" gösterilir. */
  boolean?: boolean;
  /** Ham değeri (örn. age_months) görüntülenecek metne çevirir. */
  format?: (value: unknown, row: ApiRecord) => string;
}

export interface ResourceConfig {
  slug: string;
  title: string;
  singularTitle: string;
  group: string;
  listEndpoint: string;
  createEndpoint: string;
  columns: ColumnConfig[];
  fields: FieldConfig[];
  /** Bu veri girişiyle ilişkili, salt-okunur raporlara hızlı erişim linkleri (bkz. lib/reports.ts). */
  relatedReports?: { slug: string; title: string }[];
}

const label =
  (key: string) =>
  (item: ApiRecord): string =>
    String(item[key] ?? '');

function formatAgeMonths(value: unknown): string {
  if (typeof value !== 'number') return '—';
  return `${value} ay`;
}

// --- Master Data (lookup) kaynakları ---
const breeds: OptionSource = { endpoint: '/animals/breeds', label: label('name') };
const genders: OptionSource = { endpoint: '/animals/genders', label: label('name') };
const birthTypes: OptionSource = { endpoint: '/animals/birth-types', label: label('name') };
const litterTypes: OptionSource = { endpoint: '/animals/litter-types', label: label('name') };
const hornStatuses: OptionSource = { endpoint: '/animals/horn-statuses', label: label('name') };
const sourceFarms: OptionSource = { endpoint: '/animals/source-farms', label: label('name') };
const entrySources: OptionSource = { endpoint: '/animals/entry-sources', label: label('name') };
const animalStatuses: OptionSource = { endpoint: '/animals/statuses', label: label('name') };
const deathReasons: OptionSource = { endpoint: '/animals/death-reasons', label: label('name') };
const penTypes: OptionSource = { endpoint: '/pens/pen-types', label: label('name') };
const penAssignmentReasons: OptionSource = { endpoint: '/pens/pen-assignment-reasons', label: label('name') };
const weighingMethods: OptionSource = { endpoint: '/weight-records/weighing-methods', label: label('name') };
const serviceMethods: OptionSource = { endpoint: '/breeding-events/service-methods', label: label('name') };
const pregnancyCheckMethods: OptionSource = { endpoint: '/breeding-events/pregnancy-check-methods', label: label('name') };
const pregnancyResults: OptionSource = { endpoint: '/breeding-events/pregnancy-results', label: label('name') };
const healthEventTypes: OptionSource = { endpoint: '/health-events/event-types', label: label('name') };
const diseases: OptionSource = { endpoint: '/health-events/diseases', label: label('name') };
const medicationTypes: OptionSource = { endpoint: '/health-events/medication-types', label: label('name') };
const dosageUnits: OptionSource = { endpoint: '/health-events/dosage-units', label: label('name') };
const feedTypes: OptionSource = { endpoint: '/feed/types', label: label('name') };
const feedUnits: OptionSource = { endpoint: '/feed/units', label: label('name') };
const saleTypes: OptionSource = { endpoint: '/sales/types', label: label('name') };
const disposalMethods: OptionSource = { endpoint: '/deaths/disposal-methods', label: label('name') };

// --- Başka kaynaklara referans (kayıt seçici) ---
const animals: OptionSource = {
  endpoint: '/animals',
  label: (a) => `${String(a.tag_number)}${a.name ? ' - ' + String(a.name) : ''}`,
};
const pens: OptionSource = { endpoint: '/pens', label: (p) => `${String(p.code)} - ${String(p.name)}` };
const sires: OptionSource = { endpoint: '/genetic-resource/sires', label: label('name') };
const semenBatches: OptionSource = {
  endpoint: '/genetic-resource/semen-batches',
  label: (b) => `${String(b.batch_no)} (${String(b.purchase_date)})`,
};
const buyers: OptionSource = { endpoint: '/sales/buyers', label: label('name') };
const feedItems: OptionSource = { endpoint: '/feed/items', label: label('name') };
const medications: OptionSource = { endpoint: '/health-events/medications', label: label('name') };
const breedingEventLabel = (e: ApiRecord): string =>
  `${e.dam_tag_number ? String(e.dam_tag_number) : '?'} — Aşım #${String(e.id)} (${String(e.service_date)})`;

const breedingEvents: OptionSource = {
  endpoint: '/breeding-events',
  label: breedingEventLabel,
};

// Gebelik kontrolu formunda kupe no'dan arama yapabilmek icin: sadece
// tohumlanip henuz kontrol edilmemis asim kayitlari (sahada operasyonu
// kolaylastirir - bkz. pregnancy-checks.breeding_event_id).
const pendingBreedingEvents: OptionSource = {
  endpoint: '/breeding-events?pending_check=true',
  label: breedingEventLabel,
};

const mainResources: ResourceConfig[] = [
  {
    slug: 'animals',
    title: 'Hayvanlar',
    singularTitle: 'Hayvan',
    group: 'Hayvanlar',
    listEndpoint: '/animals',
    createEndpoint: '/animals',
    columns: [
      { key: 'tag_number', label: 'Küpe No' },
      { key: 'name', label: 'İsim' },
      { key: 'breed_id', label: 'Irk', lookup: breeds },
      { key: 'gender_id', label: 'Cinsiyet', lookup: genders },
      { key: 'age_months', label: 'Yaş', format: formatAgeMonths },
      { key: 'status_id', label: 'Statü', lookup: animalStatuses },
      { key: 'entry_date', label: 'Giriş Tarihi' },
    ],
    fields: [
      { name: 'tag_number', label: 'Küpe No', type: 'text', required: true },
      { name: 'rfid', label: 'RFID', type: 'text' },
      { name: 'name', label: 'İsim', type: 'text' },
      { name: 'birth_date', label: 'Doğum Tarihi', type: 'date' },
      { name: 'birth_type_id', label: 'Doğum Şekli', type: 'select', options: birthTypes },
      { name: 'birth_weight_kg', label: 'Doğum Ağırlığı (kg)', type: 'decimal' },
      { name: 'litter_type_id', label: 'Doğum Tipi', type: 'select', options: litterTypes },
      { name: 'mother_id', label: 'Anne', type: 'select', options: animals },
      { name: 'father_sire_id', label: 'Baba (Boğa)', type: 'select', options: sires },
      { name: 'breed_id', label: 'Irk', type: 'select', options: breeds },
      { name: 'crossbreed_ratio', label: 'Melez Oranı (%)', type: 'decimal' },
      { name: 'gender_id', label: 'Cinsiyet', type: 'select', options: genders, required: true },
      { name: 'horn_status_id', label: 'Boynuz Durumu', type: 'select', options: hornStatuses },
      { name: 'entry_date', label: 'İşletmeye Giriş Tarihi', type: 'date', required: true },
      { name: 'source_farm_id', label: 'Geldiği İşletme', type: 'select', options: sourceFarms },
      { name: 'entry_source_id', label: 'Giriş Kaynağı', type: 'select', options: entrySources, required: true },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
    relatedReports: [
      { slug: 'active-animals', title: 'Aktif Hayvanlar' },
      { slug: 'calves', title: 'Buzağı Listesi (0-7 Ay)' },
      { slug: 'heifers-steers', title: 'Düve ve Dana Listesi (7-12 Ay)' },
    ],
  },
  {
    slug: 'pens',
    title: 'Padoklar',
    singularTitle: 'Padok',
    group: 'Padoklar',
    listEndpoint: '/pens',
    createEndpoint: '/pens',
    columns: [
      { key: 'code', label: 'Kod' },
      { key: 'name', label: 'Ad' },
      { key: 'pen_type_id', label: 'Tip', lookup: penTypes },
      { key: 'capacity', label: 'Kapasite' },
    ],
    fields: [
      { name: 'code', label: 'Kod', type: 'text', required: true },
      { name: 'name', label: 'Ad', type: 'text', required: true },
      { name: 'pen_type_id', label: 'Tip', type: 'select', options: penTypes, required: true },
      { name: 'capacity', label: 'Kapasite', type: 'number' },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
    relatedReports: [{ slug: 'pen-occupancy', title: 'Padok Doluluk Durumu' }],
  },
  {
    slug: 'pen-assignments',
    title: 'Padok Atamaları',
    singularTitle: 'Padok Ataması',
    group: 'Padoklar',
    listEndpoint: '/pens/assignments',
    createEndpoint: '/pens/assignments',
    columns: [
      { key: 'animal_id', label: 'Hayvan', lookup: animals },
      { key: 'pen_id', label: 'Padok', lookup: pens },
      { key: 'assigned_date', label: 'Atama Tarihi' },
      { key: 'removed_date', label: 'Çıkış Tarihi' },
      { key: 'reason_id', label: 'Neden', lookup: penAssignmentReasons },
    ],
    fields: [
      { name: 'animal_id', label: 'Hayvan', type: 'select', options: animals, required: true },
      { name: 'pen_id', label: 'Padok', type: 'select', options: pens, required: true },
      { name: 'assigned_date', label: 'Atama Tarihi', type: 'date', required: true },
      { name: 'reason_id', label: 'Neden', type: 'select', options: penAssignmentReasons, required: true },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
  },
  {
    slug: 'sires',
    title: 'Boğalar',
    singularTitle: 'Boğa',
    group: 'Genetik Kaynak',
    listEndpoint: '/genetic-resource/sires',
    createEndpoint: '/genetic-resource/sires',
    columns: [
      { key: 'name', label: 'Ad' },
      { key: 'registry_no', label: 'Tescil No' },
      { key: 'breed_id', label: 'Irk', lookup: breeds },
      { key: 'is_external', label: 'Dış Kaynak', boolean: true },
    ],
    fields: [
      { name: 'name', label: 'Ad', type: 'text', required: true },
      { name: 'registry_no', label: 'Tescil No', type: 'text' },
      { name: 'breed_id', label: 'Irk', type: 'select', options: breeds, required: true },
      { name: 'animal_id', label: 'Sürüdeki Hayvan (varsa)', type: 'select', options: animals },
      { name: 'is_external', label: 'Dış Kaynak (İşletme Dışı)', type: 'checkbox', defaultValue: 'true' },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
  },
  {
    slug: 'semen-batches',
    title: 'Sperma Stokları',
    singularTitle: 'Sperma Partisi',
    group: 'Genetik Kaynak',
    listEndpoint: '/genetic-resource/semen-batches',
    createEndpoint: '/genetic-resource/semen-batches',
    columns: [
      { key: 'sire_id', label: 'Boğa', lookup: sires },
      { key: 'batch_no', label: 'Parti No' },
      { key: 'purchase_date', label: 'Alım Tarihi' },
      { key: 'straw_count', label: 'Straw Adedi' },
    ],
    fields: [
      { name: 'sire_id', label: 'Boğa', type: 'select', options: sires, required: true },
      { name: 'batch_no', label: 'Parti No', type: 'text', required: true },
      { name: 'supplier_farm_id', label: 'Tedarikçi İşletme', type: 'select', options: sourceFarms },
      { name: 'purchase_date', label: 'Alım Tarihi', type: 'date', required: true },
      { name: 'straw_count', label: 'Straw Adedi', type: 'number', required: true },
      { name: 'storage_location', label: 'Depolama Konumu', type: 'text' },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
  },
  {
    slug: 'weight-records',
    title: 'Tartılar',
    singularTitle: 'Tartı Kaydı',
    group: 'Tartı',
    listEndpoint: '/weight-records',
    createEndpoint: '/weight-records',
    columns: [
      { key: 'animal_id', label: 'Hayvan', lookup: animals },
      { key: 'weigh_date', label: 'Tarih' },
      { key: 'weight_kg', label: 'Ağırlık (kg)' },
      { key: 'weighing_method_id', label: 'Yöntem', lookup: weighingMethods },
    ],
    fields: [
      { name: 'animal_id', label: 'Hayvan', type: 'select', options: animals, required: true },
      { name: 'weigh_date', label: 'Tarih', type: 'date', required: true },
      { name: 'weight_kg', label: 'Ağırlık (kg)', type: 'decimal', required: true },
      { name: 'weighing_method_id', label: 'Tartı Yöntemi', type: 'select', options: weighingMethods, required: true },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
  },
  {
    slug: 'breeding-events',
    title: 'Aşım Kayıtları',
    singularTitle: 'Aşım Kaydı',
    group: 'Üreme',
    listEndpoint: '/breeding-events',
    createEndpoint: '/breeding-events',
    columns: [
      { key: 'dam_id', label: 'Anne Adayı', lookup: animals },
      { key: 'service_method_id', label: 'Yöntem', lookup: serviceMethods },
      { key: 'service_date', label: 'Tarih' },
    ],
    fields: [
      { name: 'dam_id', label: 'Anne Adayı', type: 'select', options: animals, required: true },
      { name: 'service_method_id', label: 'Aşım Yöntemi', type: 'select', options: serviceMethods, required: true },
      { name: 'service_date', label: 'Tarih', type: 'date', required: true },
      { name: 'sire_animal_id', label: 'Boğa (Doğal Aşım — sürüden)', type: 'select', options: animals },
      { name: 'semen_batch_id', label: 'Sperma Partisi (Suni Tohumlama)', type: 'select', options: semenBatches },
      { name: 'note', label: 'Not (Doğal Aşım ise Boğa, Suni Tohumlama ise Sperma Partisi seçin — sadece biri)', type: 'textarea' },
    ],
    relatedReports: [
      { slug: 'breeding-candidates', title: 'Tohumlanacak Hayvanlar' },
      { slug: 'bred-animals', title: 'Tohumlu Hayvanlar' },
      { slug: 'repeat-breeders', title: 'Tekrar Kızgınlık / Boş Çıkanlar' },
    ],
  },
  {
    slug: 'pregnancy-checks',
    title: 'Gebelik Kontrolleri',
    singularTitle: 'Gebelik Kontrolü',
    group: 'Üreme',
    listEndpoint: '/breeding-events/pregnancy-checks',
    createEndpoint: '/breeding-events/pregnancy-checks',
    columns: [
      { key: 'breeding_event_id', label: 'Aşım Kaydı', lookup: breedingEvents },
      { key: 'check_date', label: 'Kontrol Tarihi' },
      { key: 'method_id', label: 'Yöntem', lookup: pregnancyCheckMethods },
      { key: 'result_id', label: 'Sonuç', lookup: pregnancyResults },
    ],
    fields: [
      { name: 'breeding_event_id', label: 'Küpe No (Tohumlanmış, Kontrol Bekleyen)', type: 'select', options: pendingBreedingEvents, required: true },
      { name: 'check_date', label: 'Kontrol Tarihi', type: 'date', required: true },
      { name: 'method_id', label: 'Kontrol Yöntemi', type: 'select', options: pregnancyCheckMethods, required: true },
      { name: 'result_id', label: 'Sonuç', type: 'select', options: pregnancyResults, required: true },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
    relatedReports: [{ slug: 'pregnant-animals', title: 'Gebe Hayvanlar' }],
  },
  {
    slug: 'health-events',
    title: 'Sağlık Olayları',
    singularTitle: 'Sağlık Olayı',
    group: 'Sağlık',
    listEndpoint: '/health-events',
    createEndpoint: '/health-events',
    columns: [
      { key: 'animal_id', label: 'Hayvan', lookup: animals },
      { key: 'event_type_id', label: 'Tip', lookup: healthEventTypes },
      { key: 'event_date', label: 'Tarih' },
      { key: 'medication_id', label: 'İlaç', lookup: medications },
    ],
    fields: [
      { name: 'animal_id', label: 'Hayvan', type: 'select', options: animals, required: true },
      { name: 'event_type_id', label: 'Olay Tipi', type: 'select', options: healthEventTypes, required: true },
      { name: 'event_date', label: 'Tarih', type: 'date', required: true },
      { name: 'disease_id', label: 'Hastalık/Tanı', type: 'select', options: diseases },
      { name: 'medication_id', label: 'İlaç', type: 'select', options: medications },
      { name: 'dosage_amount', label: 'Doz Miktarı', type: 'decimal' },
      { name: 'dosage_unit_id', label: 'Doz Birimi', type: 'select', options: dosageUnits },
      { name: 'veterinarian_note', label: 'Veteriner Notu', type: 'textarea' },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
  },
  {
    slug: 'medications',
    title: 'İlaçlar',
    singularTitle: 'İlaç',
    group: 'Sağlık',
    listEndpoint: '/health-events/medications',
    createEndpoint: '/health-events/medications',
    columns: [
      { key: 'name', label: 'Ad' },
      { key: 'active_ingredient', label: 'Etken Madde' },
      { key: 'medication_type_id', label: 'Tip', lookup: medicationTypes },
      { key: 'withdrawal_period_days', label: 'Arınma Süresi (gün)' },
    ],
    fields: [
      { name: 'name', label: 'Ad', type: 'text', required: true },
      { name: 'active_ingredient', label: 'Etken Madde', type: 'text' },
      { name: 'medication_type_id', label: 'Tip', type: 'select', options: medicationTypes, required: true },
      { name: 'withdrawal_period_days', label: 'Arınma Süresi (gün)', type: 'number', defaultValue: '0' },
    ],
  },
  {
    slug: 'feed-items',
    title: 'Yem Ürünleri',
    singularTitle: 'Yem Ürünü',
    group: 'Yem',
    listEndpoint: '/feed/items',
    createEndpoint: '/feed/items',
    columns: [
      { key: 'name', label: 'Ad' },
      { key: 'feed_type_id', label: 'Tip', lookup: feedTypes },
      { key: 'default_unit_id', label: 'Birim', lookup: feedUnits },
    ],
    fields: [
      { name: 'name', label: 'Ad', type: 'text', required: true },
      { name: 'feed_type_id', label: 'Yem Tipi', type: 'select', options: feedTypes, required: true },
      { name: 'default_unit_id', label: 'Birim', type: 'select', options: feedUnits, required: true },
    ],
  },
  {
    slug: 'feed-distributions',
    title: 'Yem Dağıtımları',
    singularTitle: 'Yem Dağıtımı',
    group: 'Yem',
    listEndpoint: '/feed/distributions',
    createEndpoint: '/feed/distributions',
    columns: [
      { key: 'pen_id', label: 'Padok', lookup: pens },
      { key: 'feed_item_id', label: 'Yem Ürünü', lookup: feedItems },
      { key: 'distribution_date', label: 'Tarih' },
      { key: 'quantity', label: 'Miktar' },
    ],
    fields: [
      { name: 'pen_id', label: 'Padok', type: 'select', options: pens, required: true },
      { name: 'feed_item_id', label: 'Yem Ürünü', type: 'select', options: feedItems, required: true },
      { name: 'distribution_date', label: 'Tarih', type: 'date', required: true },
      { name: 'quantity', label: 'Miktar', type: 'decimal', required: true },
      { name: 'unit_id', label: 'Birim', type: 'select', options: feedUnits, required: true },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
  },
  {
    slug: 'buyers',
    title: 'Alıcılar',
    singularTitle: 'Alıcı',
    group: 'Satış',
    listEndpoint: '/sales/buyers',
    createEndpoint: '/sales/buyers',
    columns: [
      { key: 'name', label: 'Ad' },
      { key: 'phone', label: 'Telefon' },
      { key: 'tax_no', label: 'Vergi No' },
    ],
    fields: [
      { name: 'name', label: 'Ad', type: 'text', required: true },
      { name: 'phone', label: 'Telefon', type: 'text' },
      { name: 'tax_no', label: 'Vergi No', type: 'text' },
      { name: 'address', label: 'Adres', type: 'textarea' },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
  },
  {
    slug: 'sales',
    title: 'Satışlar',
    singularTitle: 'Satış',
    group: 'Satış',
    listEndpoint: '/sales',
    createEndpoint: '/sales',
    columns: [
      { key: 'animal_id', label: 'Hayvan', lookup: animals },
      { key: 'sale_date', label: 'Tarih' },
      { key: 'buyer_id', label: 'Alıcı', lookup: buyers },
      { key: 'sale_type_id', label: 'Tip', lookup: saleTypes },
      { key: 'total_amount', label: 'Tutar' },
    ],
    fields: [
      { name: 'animal_id', label: 'Hayvan', type: 'select', options: animals, required: true },
      { name: 'sale_date', label: 'Tarih', type: 'date', required: true },
      { name: 'buyer_id', label: 'Alıcı', type: 'select', options: buyers, required: true },
      { name: 'sale_type_id', label: 'Satış Tipi', type: 'select', options: saleTypes, required: true },
      { name: 'sale_weight_kg', label: 'Satış Ağırlığı (kg)', type: 'decimal' },
      { name: 'total_amount', label: 'Toplam Tutar', type: 'decimal', required: true },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
  },
  {
    slug: 'deaths',
    title: 'Ölümler',
    singularTitle: 'Ölüm Kaydı',
    group: 'Ölüm',
    listEndpoint: '/deaths',
    createEndpoint: '/deaths',
    columns: [
      { key: 'animal_id', label: 'Hayvan', lookup: animals },
      { key: 'death_date', label: 'Tarih' },
      { key: 'death_reason_id', label: 'Neden', lookup: deathReasons },
      { key: 'disposal_method_id', label: 'İmha Yöntemi', lookup: disposalMethods },
    ],
    fields: [
      { name: 'animal_id', label: 'Hayvan', type: 'select', options: animals, required: true },
      { name: 'death_date', label: 'Tarih', type: 'date', required: true },
      { name: 'death_reason_id', label: 'Ölüm Nedeni', type: 'select', options: deathReasons, required: true },
      { name: 'disposal_method_id', label: 'İmha Yöntemi', type: 'select', options: disposalMethods, required: true },
      { name: 'necropsy_performed', label: 'Otopsi Yapıldı mı', type: 'checkbox' },
      { name: 'note', label: 'Not', type: 'textarea' },
    ],
  },
];

// --- Master Data (lookup) tablolarinin tam CRUD kaynaklari ---
// Hepsi ayni sekle sahip (code, name, is_active) oldugu icin elle 23 kez
// tekrar yazmak yerine kucuk bir tanim listesinden uretiliyor.
interface LookupResourceDef {
  slug: string;
  title: string;
  singularTitle: string;
  group: string;
  endpoint: string;
}

const lookupDefs: LookupResourceDef[] = [
  { slug: 'breeds', title: 'Irklar', singularTitle: 'Irk', group: 'Hayvanlar', endpoint: '/animals/breeds' },
  { slug: 'genders', title: 'Cinsiyetler', singularTitle: 'Cinsiyet', group: 'Hayvanlar', endpoint: '/animals/genders' },
  { slug: 'birth-types', title: 'Doğum Şekilleri', singularTitle: 'Doğum Şekli', group: 'Hayvanlar', endpoint: '/animals/birth-types' },
  { slug: 'litter-types', title: 'Doğum Tipleri', singularTitle: 'Doğum Tipi', group: 'Hayvanlar', endpoint: '/animals/litter-types' },
  { slug: 'horn-statuses', title: 'Boynuz Durumları', singularTitle: 'Boynuz Durumu', group: 'Hayvanlar', endpoint: '/animals/horn-statuses' },
  { slug: 'source-farms', title: 'Kaynak İşletmeler', singularTitle: 'Kaynak İşletme', group: 'Hayvanlar', endpoint: '/animals/source-farms' },
  { slug: 'entry-sources', title: 'Giriş Kaynakları', singularTitle: 'Giriş Kaynağı', group: 'Hayvanlar', endpoint: '/animals/entry-sources' },
  { slug: 'animal-statuses', title: 'Hayvan Statüleri', singularTitle: 'Statü', group: 'Hayvanlar', endpoint: '/animals/statuses' },
  { slug: 'death-reasons', title: 'Ölüm Nedenleri', singularTitle: 'Ölüm Nedeni', group: 'Hayvanlar', endpoint: '/animals/death-reasons' },
  { slug: 'pen-types', title: 'Padok Tipleri', singularTitle: 'Padok Tipi', group: 'Padoklar', endpoint: '/pens/pen-types' },
  { slug: 'pen-assignment-reasons', title: 'Padok Değişim Nedenleri', singularTitle: 'Değişim Nedeni', group: 'Padoklar', endpoint: '/pens/pen-assignment-reasons' },
  { slug: 'weighing-methods', title: 'Tartı Yöntemleri', singularTitle: 'Tartı Yöntemi', group: 'Tartı', endpoint: '/weight-records/weighing-methods' },
  { slug: 'service-methods', title: 'Aşım Yöntemleri', singularTitle: 'Aşım Yöntemi', group: 'Üreme', endpoint: '/breeding-events/service-methods' },
  { slug: 'pregnancy-check-methods', title: 'Gebelik Kontrol Yöntemleri', singularTitle: 'Kontrol Yöntemi', group: 'Üreme', endpoint: '/breeding-events/pregnancy-check-methods' },
  { slug: 'pregnancy-results', title: 'Gebelik Sonuçları', singularTitle: 'Sonuç', group: 'Üreme', endpoint: '/breeding-events/pregnancy-results' },
  { slug: 'health-event-types', title: 'Sağlık Olayı Tipleri', singularTitle: 'Olay Tipi', group: 'Sağlık', endpoint: '/health-events/event-types' },
  { slug: 'diseases', title: 'Hastalıklar', singularTitle: 'Hastalık', group: 'Sağlık', endpoint: '/health-events/diseases' },
  { slug: 'medication-types', title: 'İlaç Tipleri', singularTitle: 'İlaç Tipi', group: 'Sağlık', endpoint: '/health-events/medication-types' },
  { slug: 'dosage-units', title: 'Doz Birimleri', singularTitle: 'Doz Birimi', group: 'Sağlık', endpoint: '/health-events/dosage-units' },
  { slug: 'feed-types', title: 'Yem Tipleri', singularTitle: 'Yem Tipi', group: 'Yem', endpoint: '/feed/types' },
  { slug: 'feed-units', title: 'Yem Birimleri', singularTitle: 'Yem Birimi', group: 'Yem', endpoint: '/feed/units' },
  { slug: 'sale-types', title: 'Satış Tipleri', singularTitle: 'Satış Tipi', group: 'Satış', endpoint: '/sales/types' },
  { slug: 'disposal-methods', title: 'İmha Yöntemleri', singularTitle: 'İmha Yöntemi', group: 'Ölüm', endpoint: '/deaths/disposal-methods' },
];

const lookupResources: ResourceConfig[] = lookupDefs.map((def) => ({
  slug: def.slug,
  title: def.title,
  singularTitle: def.singularTitle,
  group: def.group,
  listEndpoint: def.endpoint,
  createEndpoint: def.endpoint,
  columns: [
    { key: 'code', label: 'Kod' },
    { key: 'name', label: 'Ad' },
    { key: 'is_active', label: 'Aktif', boolean: true },
  ],
  fields: [
    { name: 'code', label: 'Kod', type: 'text', required: true },
    { name: 'name', label: 'Ad', type: 'text', required: true },
    { name: 'is_active', label: 'Aktif', type: 'checkbox', defaultValue: 'true' },
  ],
}));

export const resources: ResourceConfig[] = [...mainResources, ...lookupResources];

export function getResource(slug: string): ResourceConfig | undefined {
  return resources.find((r) => r.slug === slug);
}

export function groupedResources(): { group: string; items: ResourceConfig[] }[] {
  const groups: { group: string; items: ResourceConfig[] }[] = [];
  for (const resource of resources) {
    let bucket = groups.find((g) => g.group === resource.group);
    if (!bucket) {
      bucket = { group: resource.group, items: [] };
      groups.push(bucket);
    }
    bucket.items.push(resource);
  }
  return groups;
}

/** Sahada en sık kullanılan veri giriş ekranlarına (+ raporlar hub'ına) menüde üstte, tek listede hızlı erişim. */
interface QuickAccessDef {
  href: string;
  label: string;
  /** Verilirse, bu resource kaydı yoksa öğe listeden düşer (link kopmasın diye). */
  resourceSlug?: string;
}

const quickAccessDefs: QuickAccessDef[] = [
  { href: '/animals', label: 'Hayvanlar', resourceSlug: 'animals' },
  { href: '/breeding-events', label: 'Aşım/Tohumlama Kayıtları', resourceSlug: 'breeding-events' },
  { href: '/pregnancy-checks', label: 'Gebelik Kontrolleri', resourceSlug: 'pregnancy-checks' },
  { href: '/weight-records', label: 'Tartılar', resourceSlug: 'weight-records' },
  { href: '/pen-assignments', label: 'Padok Atamaları', resourceSlug: 'pen-assignments' },
  { href: '/health-events', label: 'Sağlık Olayları', resourceSlug: 'health-events' },
  { href: '/reports', label: 'Raporlar' },
];

export function quickAccessResources(): { href: string; label: string }[] {
  return quickAccessDefs.filter((item) => !item.resourceSlug || getResource(item.resourceSlug) !== undefined);
}
