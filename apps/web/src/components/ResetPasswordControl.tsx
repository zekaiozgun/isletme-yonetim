'use client';

import { useActionState, useState } from 'react';

export type FormState = { error?: string } | null;

interface ResetPasswordControlProps {
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
}

/** YONETICI'nin bir kullanicinin sifresini mevcut sifreyi bilmeden sifirlamasi
 * - varsayilan olarak sadece bir buton, tiklaninca yerinde kucuk bir forma
 * acilir (tablo satirini gereksiz genisletmemek icin). */
export function ResetPasswordControl({ action }: ResetPasswordControlProps) {
  const [open, setOpen] = useState(false);
  const [state, formAction, pending] = useActionState<FormState, FormData>(action, null);

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        Şifre Sıfırla
      </button>
    );
  }

  return (
    <form action={formAction} className="flex flex-wrap items-center gap-2">
      <input
        type="password"
        name="new_password"
        required
        autoFocus
        placeholder="Yeni şifre"
        className="w-32 rounded border border-slate-300 px-2 py-1 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
      />
      <button
        type="submit"
        disabled={pending}
        className="rounded bg-slate-900 px-2 py-1 text-xs font-medium text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {pending ? 'Kaydediliyor...' : 'Kaydet'}
      </button>
      <button type="button" onClick={() => setOpen(false)} className="text-xs text-slate-500 hover:underline">
        Vazgeç
      </button>
      {state?.error && <span className="w-full text-xs text-red-600">{state.error}</span>}
    </form>
  );
}
