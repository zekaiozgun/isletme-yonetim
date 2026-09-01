'use client';

import { checkInbreedingAction } from '@/lib/actions';
import { ResourceForm, type ClientFieldConfig, type FormState } from './ResourceForm';

interface SelectOption {
  value: string;
  label: string;
}

/** Aşım Kaydı formu için ResourceForm'un ince bir sarmalayıcısı - PAYLAŞILAN
 * ResourceForm bileşenine dokunmadan, sadece bu kaynağa özel akrabalık
 * kontrolünü Kaydet anında (ayrı bir widget yerine) devreye sokar. Anne
 * adayı ve boğa/sperma partisi zaten formun kendi alanları - kontrol için
 * ikinci bir seçim istenmez (bkz. kullanıcı geri bildirimi: eski
 * InbreedingCheckWidget aynı bilgiyi tekrar sordurduğu için kullanılmıyordu).
 * Sistem hiçbir şeyi ENGELLEMEZ - aşım zaten gerçekleşmiş bir olay olduğu
 * için sadece bilgilendirir, kayıt onayla devam eder (bkz. Faz 4 kural
 * seti - proje hafızası). */
export function BreedingEventForm({
  fields,
  options,
  action,
  submitLabel,
  redirectTo,
  warningField,
}: {
  fields: ClientFieldConfig[];
  options: Record<string, SelectOption[]>;
  action: (prevState: FormState, formData: FormData) => Promise<FormState>;
  submitLabel: string;
  redirectTo?: string;
  warningField?: { fieldName: string; matchValues: string[]; message: string };
}) {
  async function actionWithInbreedingCheck(prevState: FormState, formData: FormData): Promise<FormState> {
    const damId = String(formData.get('dam_id') ?? '');
    const sireAnimalId = String(formData.get('sire_animal_id') ?? '');
    const semenBatchIdRaw = String(formData.get('semen_batch_id') ?? '');

    if (damId && (sireAnimalId || semenBatchIdRaw)) {
      const outcome = await checkInbreedingAction(
        damId,
        sireAnimalId || null,
        semenBatchIdRaw ? Number(semenBatchIdRaw) : null
      );
      if (outcome.data?.hasCommonAncestor) {
        const proceed = window.confirm(
          `⚠ Ortak ata bulundu: ${outcome.data.commonAncestorNames.join(', ')}\n\n` +
            'Bu, seçtiğiniz anne ile boğa/sperma partisi arasında yakın akrabalık olabileceği anlamına gelir. ' +
            'Aşım zaten gerçekleşmiş bir olay olduğu için bu sadece bilgilendirme amaçlıdır — kaydı onaylayarak devam edebilirsiniz.\n\n' +
            'Devam edilsin mi?'
        );
        if (!proceed) return prevState;
      }
    }

    return action(prevState, formData);
  }

  return (
    <ResourceForm
      fields={fields}
      options={options}
      action={actionWithInbreedingCheck}
      submitLabel={submitLabel}
      redirectTo={redirectTo}
      warningField={warningField}
    />
  );
}
