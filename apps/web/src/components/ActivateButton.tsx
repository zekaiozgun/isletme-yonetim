'use client';

import { useActionState } from 'react';

export type FormState = { error?: string } | null;

interface ActivateButtonProps {
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
  label?: string;
  pendingLabel?: string;
}

/** Pasifleştirilen bir kaydı geri aktifleştirir - yıkıcı olmadığı icin
 * DeleteButton'ın aksine onay penceresi istemez. */
export function ActivateButton({ action, label = 'Aktifleştir', pendingLabel = 'Aktifleştiriliyor...' }: ActivateButtonProps) {
  const [state, formAction, pending] = useActionState<FormState, FormData>(action, null);

  return (
    <form action={formAction}>
      {state?.error && (
        <div className="mb-2 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</div>
      )}
      <button
        type="submit"
        disabled={pending}
        className="rounded border border-emerald-300 px-4 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50 disabled:opacity-50"
      >
        {pending ? pendingLabel : label}
      </button>
    </form>
  );
}
