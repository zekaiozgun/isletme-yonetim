import type { ClientFieldConfig } from '@/components/ResourceForm';
import { apiGetSafe, type ApiRecord } from './api';
import type { ResourceConfig } from './resources';

/**
 * new/ ve [id]/ sayfalarinin ikisinde de kullanilan ortak hazirlik:
 * select alanlarinin secenek listelerini (lookup/kayit) fetch eder ve
 * FieldConfig'i Client Component'e gecebilir (serilestirilebilir) hale
 * getirir (options.label fonksiyonu server'da kalir).
 */
export async function loadFormOptions(
  resource: ResourceConfig,
  currentValues?: ApiRecord
): Promise<{
  options: Record<string, { value: string; label: string }[]>;
  clientFields: ClientFieldConfig[];
}> {
  const optionEndpoints = Array.from(
    new Set(resource.fields.filter((field) => field.options).map((field) => field.options!.endpoint))
  );

  const optionEntries = await Promise.all(
    optionEndpoints.map(async (endpoint) => {
      const field = resource.fields.find((f) => f.options?.endpoint === endpoint)!;
      const source = field.options!;
      const items = await apiGetSafe<ApiRecord[]>(endpoint, []);
      const opts = items.map((item) => ({
        value: source.value ? source.value(item) : String(item.id),
        label: source.label(item),
      }));

      // Duzenleme modunda: mevcut kaydin secili degeri, filtrelenmis bir
      // secenek listesinde (orn. "sadece kontrol bekleyenler") artik
      // bulunmuyorsa secim kutusundan kaybolmasin diye tek kayit olarak
      // ayrica cekilip listeye eklenir.
      const currentValue = currentValues?.[field.name];
      if (currentValue !== undefined && currentValue !== null && !opts.some((o) => o.value === String(currentValue))) {
        const baseEndpoint = endpoint.split('?')[0];
        const current = await apiGetSafe<ApiRecord | null>(`${baseEndpoint}/${String(currentValue)}`, null);
        if (current) {
          opts.unshift({
            value: source.value ? source.value(current) : String(current.id),
            label: source.label(current),
          });
        }
      }

      return [endpoint, opts] as const;
    })
  );
  const options = Object.fromEntries(optionEntries);

  const clientFields: ClientFieldConfig[] = resource.fields.map((field) => ({
    name: field.name,
    label: field.label,
    type: field.type,
    required: field.required,
    defaultValue: field.defaultValue,
    optionsEndpoint: field.options?.endpoint,
  }));

  return { options, clientFields };
}
