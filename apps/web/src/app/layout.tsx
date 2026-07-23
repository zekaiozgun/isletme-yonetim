import type { Metadata } from 'next';
import './globals.css';

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
      <body className="min-h-full">{children}</body>
    </html>
  );
}
