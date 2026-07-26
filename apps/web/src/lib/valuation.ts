'use server';

import { revalidatePath } from 'next/cache';
import { apiPut } from './api';

export type SaveCheckpointsFormState = { error?: string } | null;

interface CheckpointCell {
  genderId: number;
  categoryCode: string;
}

/** Formdaki HER hücre (erkek_AGE_3, disi_GEBE, ...) - bkz. growth-valuation-checkpoints/page.tsx. */
function cellsFor(erkekId: number, disiId: number): { field: string; genderId: number; categoryCode: string }[] {
  const ageCategories = ['AGE_3', 'AGE_6', 'AGE_9', 'AGE_12'];
  const cells: { field: string; genderId: number; categoryCode: string }[] = [];
  for (const code of ageCategories) {
    cells.push({ field: `erkek_${code}`, genderId: erkekId, categoryCode: code });
    cells.push({ field: `disi_${code}`, genderId: disiId, categoryCode: code });
  }
  cells.push({ field: 'disi_GEBE', genderId: disiId, categoryCode: 'GEBE' });
  cells.push({ field: 'disi_BOS', genderId: disiId, categoryCode: 'BOS' });
  return cells;
}

export async function saveGrowthValuationCheckpointsAction(
  erkekId: number,
  disiId: number,
  _prevState: SaveCheckpointsFormState,
  formData: FormData
): Promise<SaveCheckpointsFormState> {
  const items = cellsFor(erkekId, disiId).map(({ genderId, categoryCode, field }) => {
    const raw = String(formData.get(field) ?? '').trim();
    return {
      gender_id: genderId,
      category_code: categoryCode,
      value_try: raw === '' ? null : raw,
    };
  });

  const result = await apiPut<unknown>('/growth-valuation-checkpoints', { items });
  if (result.error !== undefined) {
    return { error: result.error };
  }

  revalidatePath('/growth-valuation-checkpoints');
  return null;
}
