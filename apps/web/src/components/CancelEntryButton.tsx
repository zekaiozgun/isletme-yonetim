'use client';

import { useActionState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

export type FormState = { error?: string; success?: true } | null;

interface CancelEntryButtonProps {
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
  confirmMessage: string;
  /** Belirtilirse, action basarili olunca (state.success) bu yola yonlendirilir
   * - bkz. lib/actions.ts basindaki not (sunucu-tarafi redirect() bazen
   * takili kaliyordu, istemci tarafi router.push() daha guvenilir). */
  redirectTo?: string;
}

/** "Hatalı Giriş İptali" icin Sil'e benzer ama kasitli olarak farkli (kehribar)
 * renklendirilmis buton - kalici silme degil, statu degisikligidir. */
export function CancelEntryButton({ action, confirmMessage, redirectTo }: CancelEntryButtonProps) {
  const [state, formAction, pending] = useActionState<FormState, FormData>(action, null);
  const router = useRouter();
  const isRedirecting = Boolean(state?.success && redirectTo);
  const navigatedRef = useRef(false);

  useEffect(() => {
    if (isRedirecting) {
      navigatedRef.current = true;
      router.push(redirectTo!);
    }
  }, [isRedirecting, redirectTo, router]);

  // Guvenlik agi: bkz. ResourceForm.tsx'teki ayni desenin dokumantasyonu -
  // istemci Server Action yanitini bazen hic islemiyor, bu yuzden
  // pending/state gecislerine degil dogrudan native submit olayina bagli
  // bir zamanlayici kurulur; normal yol zamaninda tetiklenirse
  // navigatedRef.current=true olur ve zamanlayici hicbir sey yapmaz.
  function handleSubmitSafetyNet() {
    if (!redirectTo) return;
    navigatedRef.current = false;
    setTimeout(() => {
      if (!navigatedRef.current) {
        window.location.href = redirectTo;
      }
    }, 6000);
  }

  return (
    <form
      action={formAction}
      onSubmit={(event) => {
        if (!window.confirm(confirmMessage)) {
          event.preventDefault();
          return;
        }
        handleSubmitSafetyNet();
      }}
    >
      {state?.error && (
        <div className="mb-2 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</div>
      )}
      <button
        type="submit"
        disabled={pending || isRedirecting}
        className="rounded border border-amber-400 px-4 py-2 text-sm font-medium text-amber-800 hover:bg-amber-50 disabled:opacity-50"
      >
        {pending || isRedirecting ? 'İşleniyor...' : 'Hatalı Giriş İptali'}
      </button>
    </form>
  );
}
