import { changePasswordAction } from '@/lib/auth';
import { ResourceForm, type ClientFieldConfig } from '@/components/ResourceForm';

const fields: ClientFieldConfig[] = [
  { name: 'current_password', label: 'Mevcut Şifre', type: 'password', required: true },
  { name: 'new_password', label: 'Yeni Şifre', type: 'password', required: true },
];

export default function ProfilePage() {
  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-slate-900">Şifremi Değiştir</h1>
      <ResourceForm fields={fields} options={{}} action={changePasswordAction} submitLabel="Şifreyi Güncelle" />
    </div>
  );
}
