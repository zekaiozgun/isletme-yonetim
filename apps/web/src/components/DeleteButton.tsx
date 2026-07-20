'use client';

import { useActionState } from 'react';

export type FormState = { error?: string } | null;

interface DeleteButtonProps {
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
  confirmMessage: string;
}

export function DeleteButton({ action, confirmMessage }: DeleteButtonProps) {
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
        className="rounded border border-red-300 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
      >
        {pending ? 'Siliniyor...' : 'Sil'}
      </button>
    </form>
  );
}
