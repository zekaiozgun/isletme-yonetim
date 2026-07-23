'use client';

import { useActionState } from 'react';
import { loginAction, type LoginFormState } from '@/lib/auth';

const inputClass =
  'w-full rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none';

export default function LoginPage() {
  const [state, formAction, pending] = useActionState<LoginFormState, FormData>(loginAction, null);

  return (
    <div className="flex min-h-full items-center justify-center bg-slate-50 px-4 py-16">
      <div className="w-full max-w-sm rounded border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="mb-1 text-lg font-semibold text-slate-900">İşletme Yönetim</h1>
        <p className="mb-6 text-sm text-slate-500">Devam etmek için giriş yapın.</p>

        <form action={formAction} className="space-y-4">
          {state?.error && (
            <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</div>
          )}

          <div>
            <label htmlFor="username" className="mb-1 block text-sm font-medium text-slate-700">
              Kullanıcı Adı
            </label>
            <input id="username" name="username" type="text" required autoFocus className={inputClass} />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700">
              Şifre
            </label>
            <input id="password" name="password" type="password" required className={inputClass} />
          </div>

          <button
            type="submit"
            disabled={pending}
            className="w-full rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
          >
            {pending ? 'Giriş yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>
      </div>
    </div>
  );
}
