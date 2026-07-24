'use client';

import { useActionState, useRef, useState } from 'react';
import type { FieldType } from '@/lib/resources';
import { formatDateDMY } from '@/lib/format';

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
  /**
   * true ise: "Incele ve Onayla" ile once girilen degerlerin bir ozeti
   * gosterilir, gercek kayit ancak ikinci "Onayla ve Kaydet" tiklamasiyla
   * tetiklenir (Calisan modunda hayvan girisi teyidi icin).
   */
  requireConfirmation?: boolean;
  /** true ise: form salt-okunur gosterilir (kilitli kayit), kaydetme yok. */
  readOnly?: boolean;
  /**
   * Belirli bir select alaninin secilen degeri matchValues icindeyse,
   * formu ENGELLEMEDEN ustunde bir uyari banner'i gosterir (orn. "bu
   * hayvan zaten gebe olarak kayitli" - aşım kaydı girerken). Sistem
   * burada bir sey VARSAYMAZ/ENGELLEMEZ, sadece celiskiyi gorunur kilar.
   */
  warningField?: {
    fieldName: string;
    matchValues: string[];
    message: string;
  };
}

const inputClass =
  'w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none disabled:bg-slate-100 disabled:text-slate-500';

export function ResourceForm({
  fields,
  options,
  action,
  submitLabel,
  initialValues,
  requireConfirmation = false,
  readOnly = false,
  warningField,
}: ResourceFormProps) {
  const [state, formAction, pending] = useActionState<FormState, FormData>(action, null);
  const [step, setStep] = useState<'form' | 'review'>('form');
  const [reviewData, setReviewData] = useState<FormData | null>(null);
  const [activeWarning, setActiveWarning] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  const showingReview = requireConfirmation && step === 'review' && reviewData !== null;

  function handleReviewClick() {
    const formEl = formRef.current;
    if (!formEl || !formEl.reportValidity()) return;
    setReviewData(new FormData(formEl));
    setStep('review');
  }

  return (
    <form ref={formRef} action={formAction} className="max-w-xl space-y-4">
      {state?.error && (
        <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</div>
      )}

      {warningField && activeWarning && (
        <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">
          {warningField.message}
        </div>
      )}

      <div className={showingReview ? 'hidden' : 'space-y-4'}>
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
              disabled={readOnly}
              onValueChange={
                warningField && field.name === warningField.fieldName
                  ? (value) => setActiveWarning(warningField.matchValues.includes(value))
                  : undefined
              }
            />
          </div>
        ))}
      </div>

      {showingReview && reviewData && (
        <div className="rounded border border-amber-300 bg-amber-50 p-4">
          <p className="mb-3 text-sm font-medium text-amber-900">
            Girdiğiniz bilgileri kontrol edin. Onayladıktan sonra bu kaydı değiştiremez ya da silemezsiniz — yanlış
            giriş olursa "Hatalı Giriş İptali" ile pasife alınır.
          </p>
          <dl className="space-y-1 text-sm">
            {fields.map((field) => (
              <div key={field.name} className="flex items-baseline justify-between gap-4 border-b border-amber-100 py-1 last:border-b-0">
                <dt className="shrink-0 text-amber-700">{field.label}</dt>
                <dd className="text-right font-medium text-amber-950">
                  {formatReviewValue(field, reviewData, options)}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {!readOnly && (
        <div className="flex gap-3">
          {showingReview && (
            <button
              type="button"
              onClick={() => setStep('form')}
              className="rounded border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Düzenle
            </button>
          )}
          {requireConfirmation && step === 'form' ? (
            <button
              type="button"
              onClick={handleReviewClick}
              className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
            >
              İncele ve Onayla
            </button>
          ) : (
            <button
              type="submit"
              disabled={pending}
              className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
            >
              {pending ? 'Kaydediliyor...' : requireConfirmation ? 'Onayla ve Kaydet' : submitLabel}
            </button>
          )}
        </div>
      )}
    </form>
  );
}

function asText(initialValue: unknown, fallback?: string): string {
  if (initialValue !== undefined && initialValue !== null) return String(initialValue);
  return fallback ?? '';
}

function formatReviewValue(
  field: ClientFieldConfig,
  formData: FormData,
  options: Record<string, SelectOption[]>
): string {
  if (field.type === 'password') return '••••••••';
  if (field.type === 'checkbox') return formData.get(field.name) === 'on' ? 'Evet' : 'Hayır';

  const raw = formData.get(field.name);
  const value = raw === null ? '' : String(raw);
  if (!value) return '—';

  if (field.type === 'date') return formatDateDMY(value);

  if (field.type === 'select' && field.optionsEndpoint) {
    const match = (options[field.optionsEndpoint] ?? []).find((o) => o.value === value);
    return match ? match.label : value;
  }

  return value;
}

function FieldInput({
  field,
  options,
  initialValue,
  disabled,
  onValueChange,
}: {
  field: ClientFieldConfig;
  options: SelectOption[];
  initialValue?: unknown;
  disabled?: boolean;
  /** Sadece belirli bir alan icin (bkz. ResourceFormProps.warningField) - degisiklikte cagrilir, secimi kontrol etmez. */
  onValueChange?: (value: string) => void;
}) {
  switch (field.type) {
    case 'select':
      return (
        <select
          id={field.name}
          name={field.name}
          required={field.required}
          disabled={disabled}
          defaultValue={asText(initialValue)}
          onChange={onValueChange ? (e) => onValueChange(e.target.value) : undefined}
          className={inputClass}
        >
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
          disabled={disabled}
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
          disabled={disabled}
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
          disabled={disabled}
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
          disabled={disabled}
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
          disabled={disabled}
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
          disabled={disabled}
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
          disabled={disabled}
          defaultValue={asText(initialValue, field.defaultValue)}
          className={inputClass}
        />
      );
  }
}
