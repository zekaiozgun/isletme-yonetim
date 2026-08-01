'use client';

import { useActionState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export type FormState = { error?: string; success?: true } | null;

interface DeleteButtonProps {
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
  confirmMessage: string;
  /** Varsayılan "Sil" - kalıcı silme olmayan işlemler için (örn. "Pasifleştir") özelleştirilebilir. */
  label?: string;
  pendingLabel?: string;
  /** Belirtilirse, action basarili olunca (state.success) bu yola yonlendirilir
   * - bkz. lib/actions.ts basindaki not (sunucu-tarafi redirect() bazen
   * takili kaliyordu, istemci tarafi router.push() daha guvenilir). */
  redirectTo?: string;
}

export function DeleteButton({
  action,
  confirmMessage,
  label = 'Sil',
  pendingLabel = 'Siliniyor...',
  redirectTo,
}: DeleteButtonProps) {
  const [state, formAction, pending] = useActionState<FormState, FormData>(action, null);
  const router = useRouter();
  const isRedirecting = Boolean(state?.success && redirectTo);

  useEffect(() => {
    if (isRedirecting) {
      router.push(redirectTo!);
    }
  }, [isRedirecting, redirectTo, router]);

  return (
    <form
      action={formAction}
      onSubmit={(event) => {
        if (!window.confirm(confirmMessage)) {
          event.preventDefault();
        }
      }}
    >
      {state?.error && (
        <div className="mb-2 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</div>
      )}
      <button
        type="submit"
        disabled={pending || isRedirecting}
        className="rounded border border-red-300 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
      >
        {pending || isRedirecting ? pendingLabel : label}
      </button>
    </form>
  );
}
