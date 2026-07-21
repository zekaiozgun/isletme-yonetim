'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { groupedResources, quickAccessResources } from '@/lib/resources';

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const quickAccess = quickAccessResources();
  const groups = groupedResources();

  return (
    <div className="space-y-5">
      <div className="border-b border-slate-200 pb-5">
        <div className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Hızlı Erişim
        </div>
        <ul className="space-y-0.5">
          {quickAccess.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                onClick={onNavigate}
                className="block rounded px-2 py-1.5 text-sm font-medium text-slate-800 hover:bg-slate-200"
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>

      <ul className="space-y-5">
        {groups.map((group) => (
          <li key={group.group}>
            <div className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
              {group.group}
            </div>
            <ul className="space-y-0.5">
              {group.items.map((resource) => (
                <li key={resource.slug}>
                  <Link
                    href={`/${resource.slug}`}
                    onClick={onNavigate}
                    className="block rounded px-2 py-1.5 text-sm text-slate-700 hover:bg-slate-200"
                  >
                    {resource.title}
                  </Link>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function Sidebar() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!open) return;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  return (
    <>
      {/* Mobil üst çubuk */}
      <header className="sticky top-0 z-30 flex h-14 shrink-0 items-center gap-3 border-b border-slate-200 bg-white px-4 lg:hidden">
        <button
          type="button"
          onClick={() => setOpen(true)}
          aria-label="Menüyü aç"
          aria-expanded={open}
          className="-ml-1.5 flex h-9 w-9 items-center justify-center rounded text-slate-600 hover:bg-slate-100"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="h-5 w-5">
            <path d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <Link href="/" className="text-base font-semibold text-slate-900">
          İşletme Yönetim
        </Link>
      </header>

      {/* Mobil karartma katmanı */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden"
          onClick={() => setOpen(false)}
          aria-hidden
        />
      )}

      {/* Mobil çekmece menü */}
      <nav
        className={`fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] transform overflow-y-auto border-r border-slate-200 bg-slate-50 p-4 transition-transform duration-200 ease-in-out lg:hidden ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="mb-6 flex items-center justify-between">
          <Link href="/" onClick={() => setOpen(false)} className="text-lg font-semibold text-slate-900">
            İşletme Yönetim
          </Link>
          <button
            type="button"
            onClick={() => setOpen(false)}
            aria-label="Menüyü kapat"
            className="flex h-8 w-8 items-center justify-center rounded text-slate-500 hover:bg-slate-200"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="h-5 w-5">
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>
        <NavLinks onNavigate={() => setOpen(false)} />
      </nav>

      {/* Masaüstü sabit kenar çubuğu */}
      <nav className="hidden w-64 shrink-0 border-r border-slate-200 bg-slate-50 p-4 lg:block">
        <Link href="/" className="mb-6 block text-lg font-semibold text-slate-900">
          İşletme Yönetim
        </Link>
        <NavLinks />
      </nav>
    </>
  );
}
