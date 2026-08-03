'use server';

import { revalidatePath } from 'next/cache';
import { apiDelete, apiPost, apiPut } from './api';
import { getResource, type FieldConfig } from './resources';

// NOT: basari durumunda BURADA redirect() cagrilmaz - istemci tarafinda
// (bkz. ResourceForm/DeleteButton/CancelEntryButton'daki redirectTo prop'u)
// state.success gorulunce router.push() ile yonlendirilir. Server Action
// icinden redirect() cagirmak normalde calisir, ama bazi kayitlarda
// "Kaydediliyor..." yazip takili kalma (kayit backend'de basariyla
// gerceklesse bile) gozlemlendi - muhtemelen redirect()'in attigi ozel
// NEXT_REDIRECT sinyalinin bir ara katman (orn. Sentry'nin action sarma
// mekanizmasi) tarafindan yutulmasi. Basari/hata durumunu acikca DONDURUP
// yonlendirmeyi istemciye birakmak, ara katmanlardan bagimsiz calisir.
export type FormState = { error?: string; success?: true } | null;

function buildPayload(fields: FieldConfig[], formData: FormData): Record<string, unknown> {
  const payload: Record<string, unknown> = {};

  for (const field of fields) {
    if (field.type === 'checkbox') {
      payload[field.name] = formData.get(field.name) === 'on';
      continue;
    }

    const raw = formData.get(field.name);
    if (raw === null || String(raw).trim() === '') continue; // opsiyonel bos alanlari gonderme

    const value = String(raw);
    if (field.type === 'number' || field.type === 'decimal') {
      payload[field.name] = Number(value);
    } else if (field.type === 'select') {
      // Lookup/kayit id'leri sayisaldir; UUID'ler (animal_id gibi) sayiya cevrilemez, string kalir.
      const asNumber = Number(value);
      payload[field.name] = Number.isNaN(asNumber) ? value : asNumber;
    } else {
      payload[field.name] = value;
    }
  }

  return payload;
}

export async function createResource(resourceSlug: string, _prevState: FormState, formData: FormData): Promise<FormState> {
  const resource = getResource(resourceSlug);
  if (!resource) {
    return { error: `Bilinmeyen kaynak: ${resourceSlug}` };
  }

  const payload = buildPayload(resource.fields, formData);
  const result = await apiPost(resource.createEndpoint, payload);

  if (result.error !== undefined) {
    return { error: result.error };
  }

  revalidatePath(`/${resource.slug}`);
  return { success: true };
}

export async function updateResource(
  resourceSlug: string,
  id: string,
  _prevState: FormState,
  formData: FormData
): Promise<FormState> {
  const resource = getResource(resourceSlug);
  if (!resource) {
    return { error: `Bilinmeyen kaynak: ${resourceSlug}` };
  }

  const payload = buildPayload(resource.fields, formData);
  const result = await apiPut(`${resource.listEndpoint}/${id}`, payload);

  if (result.error !== undefined) {
    return { error: result.error };
  }

  revalidatePath(`/${resource.slug}`);
  return { success: true };
}

export async function deleteResource(
  resourceSlug: string,
  id: string,
  _prevState: FormState,
  _formData: FormData
): Promise<FormState> {
  const resource = getResource(resourceSlug);
  if (!resource) {
    return { error: `Bilinmeyen kaynak: ${resourceSlug}` };
  }

  const result = await apiDelete(`${resource.listEndpoint}/${id}`);

  if (result.error !== undefined) {
    return { error: result.error };
  }

  revalidatePath(`/${resource.slug}`);
  return { success: true };
}

export interface BulkWeightEntry {
  animalId: string;
  tagNumber: string;
  weightKg: number;
}

export interface BulkWeightResult {
  success: number;
  failed: { tagNumber: string; error: string }[];
}

/** Toplu tartı girişi: her satır, mevcut tekli POST /weight-records
 * endpoint'ine ayrı ayrı gönderilir (yeni bir backend endpoint'i yok,
 * ayni dogrulama/is kurallari tekrar kullanilir). Bir/birkac satir
 * basarisiz olsa da digerleri kaydedilmis olarak kalir - hepsi ya da
 * hicbiri degildir, kullanici basarisiz olanlari tek tek gorup tekrar
 * dener (bkz. components/BulkWeightForm.tsx). */
export async function bulkCreateWeightRecords(
  weighDate: string,
  weighingMethodId: number,
  entries: BulkWeightEntry[]
): Promise<BulkWeightResult> {
  const failed: { tagNumber: string; error: string }[] = [];
  let success = 0;

  for (const entry of entries) {
    const result = await apiPost('/weight-records', {
      animal_id: entry.animalId,
      weigh_date: weighDate,
      weight_kg: entry.weightKg,
      weighing_method_id: weighingMethodId,
    });
    if (result.error !== undefined) {
      failed.push({ tagNumber: entry.tagNumber, error: result.error });
    } else {
      success += 1;
    }
  }

  revalidatePath('/weight-records');
  return { success, failed };
}

export interface BulkPregnancyCheckEntry {
  breedingEventId: number;
  tagNumber: string;
  resultId: number;
}

export interface BulkPregnancyCheckResult {
  success: number;
  failed: { tagNumber: string; error: string }[];
}

/** Toplu gebelik kontrolu girisi: bulkCreateWeightRecords ile ayni desen -
 * her satir mevcut tekli POST /breeding-events/pregnancy-checks
 * endpoint'ine ayrı ayrı gonderilir, yeni bir backend endpoint'i yok (bkz.
 * components/BulkPregnancyCheckForm.tsx). */
export async function bulkCreatePregnancyChecks(
  checkDate: string,
  methodId: number,
  entries: BulkPregnancyCheckEntry[]
): Promise<BulkPregnancyCheckResult> {
  const failed: { tagNumber: string; error: string }[] = [];
  let success = 0;

  for (const entry of entries) {
    const result = await apiPost('/breeding-events/pregnancy-checks', {
      breeding_event_id: entry.breedingEventId,
      check_date: checkDate,
      method_id: methodId,
      result_id: entry.resultId,
    });
    if (result.error !== undefined) {
      failed.push({ tagNumber: entry.tagNumber, error: result.error });
    } else {
      success += 1;
    }
  }

  revalidatePath('/pregnancy-checks');
  return { success, failed };
}

export interface BulkHealthEventShared {
  eventTypeId: number;
  eventDate: string;
  diseaseId: number | null;
  medicationId: number | null;
  dosageAmount: number | null;
  dosageUnitId: number | null;
  veterinarianNote: string | null;
  cost: number | null;
  note: string | null;
}

export interface BulkHealthEventResult {
  success: number;
  failed: { tagNumber: string; error: string }[];
}

/** Toplu sağlık olayı girişi: bulkCreateWeightRecords ile aynı desen ama
 * ters - orada tarih/yöntem ortak, kilo hayvana özeldi; burada TÜM alanlar
 * ortak (aynı aşı/ilaç turu), sadece HANGİ hayvanların dahil olduğu
 * değişir (bkz. components/BulkHealthEventForm.tsx). Yeni backend
 * endpoint'i yok, mevcut tekli POST /health-events tekrar kullanılır. */
export async function bulkCreateHealthEvents(
  shared: BulkHealthEventShared,
  animals: { animalId: string; tagNumber: string }[]
): Promise<BulkHealthEventResult> {
  const failed: { tagNumber: string; error: string }[] = [];
  let success = 0;

  for (const animal of animals) {
    const result = await apiPost('/health-events', {
      animal_id: animal.animalId,
      event_type_id: shared.eventTypeId,
      event_date: shared.eventDate,
      disease_id: shared.diseaseId,
      medication_id: shared.medicationId,
      dosage_amount: shared.dosageAmount,
      dosage_unit_id: shared.dosageUnitId,
      veterinarian_note: shared.veterinarianNote,
      cost: shared.cost,
      note: shared.note,
    });
    if (result.error !== undefined) {
      failed.push({ tagNumber: animal.tagNumber, error: result.error });
    } else {
      success += 1;
    }
  }

  revalidatePath('/health-events');
  return { success, failed };
}

export interface BulkPenAssignmentShared {
  penId: number;
  assignedDate: string;
  reasonId: number;
  note: string | null;
}

export interface BulkPenAssignmentResult {
  success: number;
  failed: { tagNumber: string; error: string }[];
}

/** Toplu padok ataması: bulkCreateHealthEvents ile aynı desen - hedef
 * padok/tarih/neden ortak, sadece hangi hayvanların taşındığı değişir
 * (bkz. components/BulkPenAssignmentForm.tsx). Yeni backend endpoint'i
 * yok, mevcut tekli POST /pens/assignments tekrar kullanılır. */
export async function bulkCreatePenAssignments(
  shared: BulkPenAssignmentShared,
  animals: { animalId: string; tagNumber: string }[]
): Promise<BulkPenAssignmentResult> {
  const failed: { tagNumber: string; error: string }[] = [];
  let success = 0;

  for (const animal of animals) {
    const result = await apiPost('/pens/assignments', {
      animal_id: animal.animalId,
      pen_id: shared.penId,
      assigned_date: shared.assignedDate,
      reason_id: shared.reasonId,
      note: shared.note,
    });
    if (result.error !== undefined) {
      failed.push({ tagNumber: animal.tagNumber, error: result.error });
    } else {
      success += 1;
    }
  }

  revalidatePath('/pen-assignments');
  return { success, failed };
}

/** "Hatalı Giriş İptali": kilitli olsa dahi hem Çalışan hem Yönetici
 * kullanabilir - hayvanı silmek yerine statüsünü değiştirir (bkz.
 * app/modules/animal service.cancel_animal_entry, PUT/DELETE ile ilgisizdir). */
export async function cancelAnimalEntryAction(
  animalId: string,
  _prevState: FormState,
  _formData: FormData
): Promise<FormState> {
  const result = await apiPost<unknown>(`/animals/${animalId}/cancel-entry`, {});

  if (result.error !== undefined) {
    return { error: result.error };
  }

  revalidatePath(`/animals/${animalId}`);
  return { success: true };
}

export interface RationItemInput {
  feedItemId: number;
  dailyQuantityPerAnimal: number;
  unitId: number;
}

/** Yeni bir padok rasyonu (donemi) baslatir - backend, ayni padogun hala
 * acik onceki rasyonunu otomatik kapatir (bkz. app/modules/feed/service.py
 * create_pen_ration). Gunluk yem dagitim kaydi YOKTUR (bkz.
 * components/RationForm.tsx). */
export async function createPenRationAction(
  penId: number,
  startDate: string,
  note: string,
  items: RationItemInput[]
): Promise<{ error?: string }> {
  const result = await apiPost('/feed/rations', {
    pen_id: penId,
    start_date: startDate,
    note: note.trim() || null,
    items: items.map((item) => ({
      feed_item_id: item.feedItemId,
      daily_quantity_per_animal: item.dailyQuantityPerAnimal,
      unit_id: item.unitId,
    })),
  });

  if (result.error !== undefined) {
    return { error: result.error };
  }

  revalidatePath('/pen-rations');
  return {};
}

export async function deletePenRationAction(
  rationId: number,
  _prevState: FormState,
  _formData: FormData
): Promise<FormState> {
  const result = await apiDelete(`/feed/rations/${rationId}`);

  if (result.error !== undefined) {
    return { error: result.error };
  }

  revalidatePath('/pen-rations');
  return { success: true };
}
