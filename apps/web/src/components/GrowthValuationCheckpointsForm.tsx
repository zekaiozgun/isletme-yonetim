'use client';

import { useActionState } from 'react';

export type SaveCheckpointsFormState = { error?: string } | null;

interface Row {
  code: string;
  label: string;
  femaleOnly?: boolean;
}

const ROWS: Row[] = [
  { code: 'AGE_3', label: '3 Aylık' },
  { code: 'AGE_6', label: '6 Aylık' },
  { code: 'AGE_9', label: '9 Aylık' },
  { code: 'AGE_12', label: '12 Aylık (Besilik Dana / Gebe Düve)' },
  { code: 'GEBE', label: 'Gebe İnek', femaleOnly: true },
  { code: 'BOS', label: 'Boş (Açık) İnek', femaleOnly: true },
];

const cellClass =
  'w-full rounded border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none';

export function GrowthValuationCheckpointsForm({
  action,
  values,
}: {
  action: (prevState: SaveCheckpointsFormState, formData: FormData) => Promise<SaveCheckpointsFormState>;
  values: Record<string, string>;
}) {
  const [state, formAction, pending] = useActionState<SaveCheckpointsFormState, FormData>(action, null);

  return (
    <form action={formAction} className="max-w-2xl space-y-4">
      {state?.error && (
        <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</div>
      )}

      <div className="overflow-x-auto rounded border border-slate-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-left text-slate-600">
              <th className="px-3 py-2 font-medium">Kategori</th>
              <th className="px-3 py-2 font-medium">Erkek (TL)</th>
              <th className="px-3 py-2 font-medium">Dişi (TL)</th>
            </tr>
          </thead>
          <tbody>
            {ROWS.map((row) => (
              <tr key={row.code} className="border-b border-slate-100 last:border-0">
                <td className="px-3 py-2 text-slate-700">{row.label}</td>
                <td className="px-3 py-2">
                  {row.femaleOnly ? (
                    <span className="text-slate-300">—</span>
                  ) : (
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      name={`erkek_${row.code}`}
                      defaultValue={values[`erkek_${row.code}`] ?? ''}
                      className={cellClass}
                    />
                  )}
                </td>
                <td className="px-3 py-2">
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    name={`disi_${row.code}`}
                    defaultValue={values[`disi_${row.code}`] ?? ''}
                    className={cellClass}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        type="submit"
        disabled={pending}
        className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {pending ? 'Kaydediliyor…' : 'Kaydet'}
      </button>
    </form>
  );
}
