import { apiGet, apiGetSafe, type ApiRecord } from '@/lib/api';
import { activateUserAction, createUserAction, deactivateUserAction, resetUserPasswordAction } from '@/lib/auth';
import { ResourceForm, type ClientFieldConfig } from '@/components/ResourceForm';
import { DeleteButton } from '@/components/DeleteButton';
import { ActivateButton } from '@/components/ActivateButton';
import { ResetPasswordControl } from '@/components/ResetPasswordControl';

interface MeResponse {
  role: 'YONETICI' | 'CALISAN';
}

interface UserRow extends ApiRecord {
  id: number;
  username: string;
  full_name: string | null;
  role: 'YONETICI' | 'CALISAN';
  is_active: boolean;
}

const ROLE_OPTIONS_KEY = 'user-role-options';

const fields: ClientFieldConfig[] = [
  { name: 'username', label: 'Kullanıcı Adı', type: 'text', required: true },
  { name: 'password', label: 'Şifre', type: 'password', required: true },
  { name: 'full_name', label: 'Ad Soyad', type: 'text' },
  { name: 'role', label: 'Rol', type: 'select', required: true, optionsEndpoint: ROLE_OPTIONS_KEY },
];

const options = {
  [ROLE_OPTIONS_KEY]: [
    { value: 'CALISAN', label: 'Çalışan' },
    { value: 'YONETICI', label: 'Yönetici' },
  ],
};

export default async function UsersPage() {
  const me = await apiGet<MeResponse>('/auth/me');

  if (me.role !== 'YONETICI') {
    return (
      <div>
        <h1 className="mb-2 text-xl font-semibold text-slate-900">Kullanıcılar</h1>
        <p className="text-sm text-slate-500">Bu sayfayı görüntülemek için yönetici yetkisi gerekiyor.</p>
      </div>
    );
  }

  const users = await apiGetSafe<UserRow[]>('/auth/users', []);

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-slate-900">Kullanıcılar</h1>

      <div className="mb-8 overflow-x-auto rounded border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Kullanıcı Adı</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Ad Soyad</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Rol</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">Durum</th>
              <th className="px-3 py-2 text-left font-medium text-slate-600">İşlemler</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {users.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-center text-slate-500">
                  Henüz kayıt yok.
                </td>
              </tr>
            )}
            {users.map((u) => (
              <tr key={u.id}>
                <td className="whitespace-nowrap px-3 py-2 text-slate-700">{u.username}</td>
                <td className="whitespace-nowrap px-3 py-2 text-slate-700">{u.full_name ?? '—'}</td>
                <td className="whitespace-nowrap px-3 py-2 text-slate-700">
                  {u.role === 'YONETICI' ? 'Yönetici' : 'Çalışan'}
                </td>
                <td className="whitespace-nowrap px-3 py-2 text-slate-700">{u.is_active ? 'Aktif' : 'Pasif'}</td>
                <td className="px-3 py-2">
                  <div className="flex flex-wrap items-center gap-2">
                    {u.is_active ? (
                      <DeleteButton
                        action={deactivateUserAction.bind(null, u.id)}
                        confirmMessage={`"${u.username}" kullanıcısını pasifleştirmek istediğinize emin misiniz? Giriş yapamaz hâle gelir, kaydı silinmez.`}
                        label="Pasifleştir"
                        pendingLabel="Pasifleştiriliyor..."
                      />
                    ) : (
                      <ActivateButton action={activateUserAction.bind(null, u.id)} />
                    )}
                    <ResetPasswordControl action={resetUserPasswordAction.bind(null, u.id)} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="mb-4 text-lg font-semibold text-slate-900">Yeni Kullanıcı Ekle</h2>
      <ResourceForm fields={fields} options={options} action={createUserAction} submitLabel="Kullanıcı Ekle" />
    </div>
  );
}
