"""Raporlama (analiz) katmani sema tanimlari.

Anayasa m.2: Veri Girisi ile Analiz/Raporlama kesin olarak ayrilir. Bu
semalar hicbir ORM modeline (Create/Read ciftine) karsilik gelmez; servis
katmaninda birden fazla modul (Animal, Breeding, Pen) birlestirilerek elle
insa edilen, salt-okunur turetilmis goruntulerdir (Anayasa m.4/m.5).
"""

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class AnimalEvaluationReportRead(BaseModel):
    id: int
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    evaluation_date: date
    direction_name: str
    reason_name: str
    priority_name: str | None = None
    note: str | None = None


class BreedingRecommendationRead(BaseModel):
    id: int
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    evaluation_date: date
    reason_name: str
    note: str | None = None


class HerdExitRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    exit_type: str
    exit_date: date
    exit_age_months: int | None = None
    herd_tenure_days: int | None = None
    # Bu hayvana ait, cikistan ONCE girilmis TUM "Suruden Cikarma" yonlu
    # degerlendirmeler - tarih sirasiyla tek metinde birlestirilir (bkz.
    # list_death_losses'taki reason_breakdown deseni).
    culling_evaluation_reasons: str | None = None
    last_evaluation_date: date | None = None
    # Son degerlendirme ile fiili cikis arasindaki gun farki - "karar-
    # uygulama gecikmesi": bekleme surecinin ne kadar uzadigini gosterir.
    decision_to_exit_days: int | None = None


class BreedingCandidateRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    birth_date: date | None = None
    age_months: int | None = None
    reason: str
    # Makine-okunabilir sabit deger: "candidate_new" | "candidate_postpartum"
    # | "open" - frontend'in gorunum metnine (reason) gore degil buna gore
    # mantik kurmasi icin (bkz. reports/service.py _BREEDING_CANDIDATE_REASONS).
    reason_code: str
    last_calving_date: date | None = None
    # Yalnizca reason="Tekrar Kızgınlık / Boş" satirlarinda dolu.
    last_service_date: date | None = None
    # "Bekleme Süresi" - HER reason'da dolar, baslangic noktasi reason'a
    # gore degisir: "Boş Çıkan"da last_service_date'ten, "Tohumlanacak
    # (Doğum Sonrası)"/"Post Partum"da last_calving_date'ten, "İlk
    # Tohumlama"da tohumlanabilir yasa (12 ay) girdigi tarihten bu yana
    # gecen gun (bkz. reports/service.py list_breeding_candidates).
    days_open: int | None = None
    # Yalnizca reason="Tekrar Kızgınlık / Boş" satirlarinda dolu.
    service_method_name: str | None = None
    # Hayvanin son dogumundan (hic dogurmadiysa girisinden) bu yana kac
    # kez tohumlandigi - fertilite sorunlarini gormek icin (bkz.
    # _service_attempt_count). "İlk Tohumlama"/"Doğum Sonrası" satirlarinda
    # 0'dir (henuz hic denenmedi).
    service_attempt_count: int = 0
    # true ise: bu hayvan, bu tohumlamadan ONCE ayni ureme dongusunde baska
    # bir tohumlamada "Gebe" olarak onaylanmisti - yeni tohumlama o
    # gebeligin artik gecerli olmadigini ima eder (bkz.
    # _returned_from_pregnancy). Sistem SEBEBI (dusuk mu, yanlis giris mi)
    # TAHMIN ETMEZ, sadece celiskiyi gorunur kilar.
    returned_from_pregnancy: bool = False
    # En son gebelik kontrolune girilen not (PregnancyCheck.note) - orn.
    # returned_from_pregnancy'nin sebebini kullanicinin elle acikladigi yer.
    note: str | None = None


class CalvingRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    birth_date: date
    gender_name: str
    birth_type_name: str | None = None
    is_difficult_birth: bool
    litter_type_name: str | None = None
    birth_weight_kg: Decimal | None = None
    mother_id: uuid.UUID | None = None
    mother_tag_number: str | None = None
    father_sire_name: str | None = None
    # Buzaginin GUNCEL statusu (Aktif/Satildi/Oldu/vb.) - dogum aninda
    # degil, rapor calistirildigi andaki durumu yansitir (Anayasa m.8).
    status_name: str
    note: str | None = None


class OffspringByMotherRead(BaseModel):
    mother_id: uuid.UUID
    mother_tag_number: str
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    birth_date: date
    gender_name: str
    status_name: str


class OffspringBySireRead(BaseModel):
    sire_id: int
    # Kimlik gosterim onceligi (frontend'de birlestirilir): kupe no
    # (suruye ait bogaysa) -> registry_no (soy kutugu kayit no, dis
    # kaynakli bogalarda girilmis olabilir) -> hicbiri yoksa sire_id
    # (sistemin ic kayit no'su) - hicbiri uydurma degildir, zaten var
    # olan bir facttir, sadece gosterim onceligi degisir.
    sire_tag_number: str | None = None
    sire_registry_no: str | None = None
    sire_name: str
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    birth_date: date
    gender_name: str
    mother_tag_number: str | None = None
    status_name: str


class MotherPerformanceRead(BaseModel):
    mother_id: uuid.UUID
    mother_tag_number: str
    offspring_count: int
    female_count: int
    male_count: int
    # En az iki tartisi olan yavrularin ortalamasi - omur boyu (tarih
    # araligi olmadan) gunluk canli agirlik artisi (ADG). Hicbir yavrunun
    # yeterli tartisi yoksa None.
    avg_daily_gain_kg: float | None = None
    # TUM yavrularin (hala aktif olanlar dahil) yuzde kaci oldu.
    loss_rate: float | None = None


class SirePerformanceRead(BaseModel):
    sire_id: int
    # Kimlik gosterim onceligi (bkz. OffspringBySireRead ile aynı mantık).
    sire_tag_number: str | None = None
    sire_registry_no: str | None = None
    sire_name: str
    offspring_count: int
    female_count: int
    male_count: int
    avg_daily_gain_kg: float | None = None
    loss_rate: float | None = None


class DeathLossReportRead(BaseModel):
    age_group: str
    death_count: int
    reason_breakdown: str
    current_active_count: int
    loss_rate: float | None = None
    # true ise bu satir buzagi+yetiskin gruplarinin BIRLESIK toplamidir -
    # dashboard'daki "Yillik Kayip Orani" (tum sürü icin tek bir oran) ile
    # dogrudan karsilastirilabilsin diye (bkz. list_death_losses).
    is_summary: bool = False


class CalvingIntervalRead(BaseModel):
    is_summary: bool = False
    animal_id: uuid.UUID | None = None
    tag_number: str
    name: str | None = None
    previous_calving_date: date | None = None
    last_calving_date: date | None = None
    interval_days: int
    calving_count: int


class FeedConsumptionRead(BaseModel):
    pen_code: str
    pen_name: str
    feed_item_name: str
    feed_type_name: str
    total_quantity_kg: float
    # Rasyonun bu aralikta fiilen uygulandigi (padogun dolu oldugu) gun
    # sayisi - eski "dagitim sayisi"nin karsiligi (bkz. models.py PenRation).
    active_days: int


class DailyRationCostRead(BaseModel):
    is_summary: bool = False
    pen_code: str
    pen_name: str
    # Guncel (as_of_date itibariyla) padoktaki yetiskin/buzagi sayisi -
    # RationItem.scope'a gore hangi kalemin kime uygulandigini gostermek
    # icin baglam saglar (bkz. reports/service.py list_daily_ration_cost).
    adult_count: int
    calf_count: int
    daily_cost_try: Decimal


class FeedStockRunwayRead(BaseModel):
    is_summary: bool = False
    feed_item_name: str
    feed_type_name: str
    stock_kg: float
    # Guncel (aktif rasyonlardan turetilen, as_of_date itibariyla) toplam
    # gunluk tuketim hizi - gecmis ortalama DEGIL, "su an bu hizda gidilirse"
    # varsayimidir (bkz. list_feed_stock_runway docstring'i).
    daily_consumption_kg: float
    days_remaining: int | None = None
    estimated_depletion_date: date | None = None


class FeedStockStatusRead(BaseModel):
    feed_item_name: str
    feed_type_name: str
    total_purchased_kg: float
    total_consumed_kg: float
    stock_kg: float
    avg_cost_per_kg_try: float | None = None
    stock_value_try: Decimal | None = None


class HerdFlowReportRead(BaseModel):
    category: str
    direction: str
    # Makine-okunabilir sabit deger: "IN" | "OUT" | "NET" - frontend'in
    # gorunum metnine (direction) gore degil buna gore mantik kurmasi icin
    # (bkz. reports/service.py list_herd_flow).
    direction_code: str
    count: int


class SalesReportRead(BaseModel):
    buyer_name: str
    # Kalem tipe gore de bolunuyor - "Canli Satis"/"Kesim Icin Satis"/
    # "Damizlik Satis" birbirinden cok farkli fiyatlama mantigina sahip
    # (bkz. list_sales_report dokumantasyonu), tek bir alici altinda
    # karistirilirsa kg basina fiyat ortalamasi anlamsizlasir.
    sale_type_name: str
    sale_count: int
    total_revenue: Decimal
    average_sale_amount: float
    total_live_weight_kg: Decimal
    average_price_per_live_kg: float | None = None
    total_carcass_weight_kg: Decimal
    average_price_per_carcass_kg: float | None = None
    # Sadece HEM canli HEM karkas agirligi girilmis satislardan (kesim
    # satislarinda ikisi de bilinebilir) - randiman: karkas/canli * 100.
    average_dressing_percentage: float | None = None


class WeightGainRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    first_weigh_date: date
    first_weight_kg: Decimal
    last_weigh_date: date
    last_weight_kg: Decimal
    days_between: int
    weight_gain_kg: Decimal
    average_daily_gain_kg: float
    note: str | None = None


class HealthEventReportRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    event_date: date
    event_type_name: str
    is_illness: bool
    disease_name: str | None = None
    medication_name: str | None = None
    dosage_amount: Decimal | None = None
    dosage_unit_name: str | None = None
    veterinarian_note: str | None = None


class PregnancyCheckResultRead(BaseModel):
    breeding_event_id: int
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    service_date: date
    check_date: date
    method_name: str
    result_name: str
    is_suspicious: bool
    note: str | None = None


class BreedingPerformanceRead(BaseModel):
    source_type: str
    source_label: str
    service_count: int
    pregnant_count: int
    open_count: int
    suspicious_count: int
    pending_count: int
    pregnancy_rate: float | None = None


class BredAnimalRead(BaseModel):
    breeding_event_id: int
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    service_date: date
    # Baba adayi TEK metinde ozetlenir (dogal asimda hayvan, suni
    # tohumlamada sperma partisi+boga) - yontemi (Dogal Asim/Suni
    # Tohumlama) zaten bu etiketten anlasilir, ayrica bir alan gerekmez
    # (bkz. service.py _breeding_event_sire_label).
    sire_label: str
    days_since_service: int
    check_status: str
    pregnancy_check_due: bool
    # service_date + GESTATION_DAYS - kontrol sonucu (Gebe) onaylanmis
    # olsun olmasin HER zaman hesaplanir (henuz onaylanmamis satirlarda
    # "tahmini", Gebe satirlarda kesinlesmis bir projeksiyon).
    expected_calving_date: date
    days_until_calving: int
    # Hayvanin son dogumundan (hic dogurmadiysa girisinden) bu yana, bu
    # dahil, kacinci tohumlama denemesi oldugu (bkz. _service_attempt_count).
    service_attempt_count: int = 1
    # true ise: bu tohumlamadan ONCE ayni ureme dongusunde baska bir
    # tohumlamada "Gebe" onayi vardi (bkz. BreedingCandidateRead'deki
    # ayni alanin aciklamasi / _returned_from_pregnancy).
    returned_from_pregnancy: bool = False
    note: str | None = None


class WithdrawalPeriodRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    medication_name: str
    event_date: date
    withdrawal_end_date: date
    days_remaining: int


class YoungAnimalRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    gender_name: str
    breed_name: str | None = None
    birth_date: date | None = None
    age_months: int | None = None
    age_days: int | None = None
    mother_tag_number: str | None = None
    father_sire_name: str | None = None
    note: str | None = None


class PenOccupancyRead(BaseModel):
    pen_id: int
    code: str
    name: str
    capacity: int | None = None
    current_count: int
    occupancy_rate: float | None = None


class HerdInventoryRead(BaseModel):
    total_active: int
    by_status: dict[str, int]
    female_active: int
    male_active: int
    calves_count: int
    heifers_steers_count: int
    breeding_age_female_count: int
    adult_male_count: int


class HerdStatusSummaryRead(BaseModel):
    category: str
    count: int
    # 0: ust seviye yas kovasi (Buzagi/Duve-Tosun/Dogurgan Disi/Yetiskin
    # Erkek/Toplam Aktif) - 1: "Dogurgan Yastaki Disi" alti ureme
    # alt-durumu (frontend'in girinti vermesi icin).
    level: int = 0
    # true ise: bu satir bir ara/genel toplamdir (Dogurgan Yastaki Disi,
    # Toplam Aktif) - frontend'in kalin gostermesi icin.
    is_total: bool = False


class PenEfficiencyRead(BaseModel):
    pen_id: int
    code: str
    name: str
    total_feed_quantity_kg: float
    total_feed_cost_try: Decimal
    total_feed_cost_usd: Decimal
    total_weight_gain_kg: Decimal
    feed_conversion_ratio: float | None = None
    cost_per_kg_gain_try: float | None = None
    cost_per_kg_gain_usd: float | None = None


class AnimalProfitabilityRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    outcome: str
    outcome_date: date
    entry_value_try: Decimal | None = None
    health_cost_try: Decimal
    feed_cost_try: Decimal
    total_cost_try: Decimal
    total_cost_usd: Decimal
    revenue_try: Decimal | None = None
    revenue_usd: Decimal | None = None
    profit_try: Decimal
    profit_usd: Decimal


class HerdCostSummaryRead(BaseModel):
    category: str
    # Makine-okunabilir sabit deger - frontend'in gorunum metnine (category)
    # gore degil buna gore mantik kurmasi icin (bkz. reports/service.py
    # list_herd_cost_summary).
    category_code: str
    amount_try: Decimal
    amount_usd: Decimal


class AnimalMarketValueRead(BaseModel):
    animal_id: uuid.UUID
    tag_number: str
    name: str | None = None
    gender_name: str
    age_months: int | None = None
    amount_try: Decimal
    amount_usd: Decimal
    # "market_estimate" (büyüme çıpalarından interpolasyon) | "cost_basis"
    # (maliyet-bazlı defter değeri) - hangi rakamın gerçek piyasa gözlemine
    # mi yoksa harcama kaydına mı dayandığını gizlemeden gösterir.
    source_code: str
    # "BUYUME" (henüz Demirbaşa geçmemiş) | "GEBE" | "BOS" (olgun dişi,
    # güncel tohumlama döngüsü durumu) | "OLGUN" (olgun erkek/boğa) -
    # hangi değerleme kovasının kullanıldığını source_code'dan bağımsız
    # olarak açıklar (bkz. reports/service.py _valuation_status_code_ctx).
    status_code: str


class DashboardSummaryRead(BaseModel):
    active_animal_count: int
    breeding_candidate_count: int
    pregnancy_check_due_count: int
    pregnant_count: int
    repeat_breeder_count: int
    calves_count: int
    heifers_steers_count: int
    pen_occupancy_rate: float | None = None
    average_calving_interval_days: float | None = None
    annual_loss_rate: float | None = None
