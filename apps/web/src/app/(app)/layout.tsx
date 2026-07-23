import { apiGet } from '@/lib/api';
import { Sidebar, type SidebarUser } from '@/components/Sidebar';

interface MeResponse {
  username: string;
  full_name: string | null;
  role: 'YONETICI' | 'CALISAN';
}

export default async function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const me = await apiGet<MeResponse>('/auth/me');
  const user: SidebarUser = { username: me.username, fullName: me.full_name, role: me.role };

  return (
    <div className="flex min-h-full flex-col lg:flex-row">
      <Sidebar user={user} />
      <main className="min-w-0 flex-1 p-4 sm:p-6">{children}</main>
    </div>
  );
}
