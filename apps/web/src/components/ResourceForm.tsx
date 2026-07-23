'use client';

import { useActionState } from 'react';
import type { FieldType } from '@/lib/resources';

export type FormState = { error?: string } | null;

interface SelectOption {
  value: string;
  label: string;
}

/**
 * FieldConfig'in Client Component'e gecebilen (serilestirilebilir) alt
 * kumesi. FieldConfig.options.label bir fonksiyondur ve React Server
 * Component sinirini gecemez - bu yuzden burada sadece optionsEndpoint
 * (string) tasinir, secenek listesi ayrica `options` prop'uyla verilir.
 */
export interface ClientFieldConfig {
  name: string;
  label: string;
  type: FieldType;
  required?: boolean;
  defaultValue?: string;
  optionsEndpoint?: string;
}

interface ResourceFormProps {
  fields: ClientFieldConfig[];
  options: Record<string, SelectOption[]>;
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
  submitLabel: string;
  /** Duzenleme modunda mevcut kaydin degerleri (varsa formu onceden doldurur). */
  initialValues?: Record<string, unknown>;
}

const inputClass =
  'w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none';

export function ResourceForm({ fields, options, action, submitLabel, initialValues }: ResourceFormProps) {
  const [state, formAction, pending] = useActionState<FormState, FormData>(action, null);

  return (
    <form action={formAction} className="max-w-xl space-y-4">
      {state?.error && (
        <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</div>
      )}

      {fields.map((field) => (
        <div key={field.name}>
          <label htmlFor={field.name} className="mb-1 block text-sm font-medium text-slate-700">
            {field.label}
            {field.required && <span className="text-red-500"> *</span>}
          </label>
          <FieldInput
            field={field}
            options={field.optionsEndpoint ? (options[field.optionsEndpoint] ?? []) : []}
            initialValue={initialValues ? initialValues[field.name] : undefined}
          />
        </div>
      ))}

      <button
        type="submit"
        disabled={pending}
        className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {pending ? 'Kaydediliyor...' : submitLabel}
      </button>
    </form>
  );
}

function asText(initialValue: unknown, fallback?: string): string {
  if (initialValue !== undefined && initialValue !== null) return String(initialValue);
  return fallback ?? '';
}

function FieldInput({
  field,
  options,
  initialValue,
}: {
  field: ClientFieldConfig;
  options: SelectOption[];
  initialValue?: unknown;
}) {
  switch (field.type) {
    case 'select':
      return (
        <select id={field.name} name={field.name} required={field.required} defaultValue={asText(initialValue)} className={inputClass}>
          <option value="" disabled>
            Seçiniz...
          </option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    case 'checkbox': {
      const checked = initialValue !== undefined ? Boolean(initialValue) : field.defaultValue === 'true';
      return (
        <input
          id={field.name}
          name={field.name}
          type="checkbox"
          defaultChecked={checked}
          className="h-4 w-4 rounded border-slate-300"
        />
      );
    }
    case 'textarea':
      return (
        <textarea
          id={field.name}
          name={field.name}
          required={field.required}
          rows={3}
          defaultValue={asText(initialValue)}
          className={inputClass}
        />
      );
    case 'date':
      return (
        <input
          id={field.name}
          name={field.name}
          type="date"
          required={field.required}
          defaultValue={asText(initialValue)}
          className={inputClass}
        />
      );
    case 'number':
      return (
        <input
          id={field.name}
          name={field.name}
          type="number"
          step="1"
          required={field.required}
          defaultValue={asText(initialValue, field.defaultValue)}
          className={inputClass}
        />
      );
    case 'decimal':
      return (
        <input
          id={field.name}
          name={field.name}
          type="number"
          step="0.01"
          required={field.required}
          defaultValue={asText(initialValue, field.defaultValue)}
          className={inputClass}
        />
      );
    case 'password':
      // Sifre alanlari asla onceki degerden doldurulmaz (yazma-amacli alan).
      return (
        <input
          id={field.name}
          name={field.name}
          type="password"
          autoComplete="new-password"
          required={field.required}
          className={inputClass}
        />
      );
    default:
      return (
        <input
          id={field.name}
          name={field.name}
          type="text"
          required={field.required}
          defaultValue={asText(initialValue, field.defaultValue)}
          className={inputClass}
        />
      );
  }
}
