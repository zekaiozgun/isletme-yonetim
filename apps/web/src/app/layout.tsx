import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'İşletme Yönetim',
  description: 'İşletme Yönetim — web application',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr" className="h-full antialiased">
      <body className="flex min-h-full">
        <Sidebar />
        <main className="min-w-0 flex-1 p-6">{children}</main>
      </body>
    </html>
  );
}
