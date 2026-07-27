'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { apiDelete, apiPost, apiPut } from './api';
import { getResource, type FieldConfig } from './resources';

export type FormState = { error?: string } | null;

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
  redirect(`/${resource.slug}`);
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
  redirect(`/${resource.slug}`);
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
  redirect(`/${resource.slug}`);
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
  redirect('/animals');
}
