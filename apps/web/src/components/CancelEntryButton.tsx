'use client';

import { useActionState } from 'react';

export type FormState = { error?: string } | null;

interface CancelEntryButtonProps {
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
  confirmMessage: string;
}

/** "Hatalı Giriş İptali" icin Sil'e benzer ama kasitli olarak farkli (kehribar)
 * renklendirilmis buton - kalici silme degil, statu degisikligidir. */
export function CancelEntryButton({ action, confirmMessage }: CancelEntryButtonProps) {
  const [state, formAction, pending] = useActionState<FormState, FormData>(action, null);

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
        disabled={pending}
        className="rounded border border-amber-400 px-4 py-2 text-sm font-medium text-amber-800 hover:bg-amber-50 disabled:opacity-50"
      >
        {pending ? 'İşleniyor...' : 'Hatalı Giriş İptali'}
      </button>
    </form>
  );
}
