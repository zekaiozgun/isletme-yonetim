'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import { groupedMainResources, groupedLookupResources, quickAccessResources } from '@/lib/resources';
import { logoutAction } from '@/lib/auth';

export interface SidebarUser {
  username: string;
  fullName: string | null;
  role: 'YONETICI' | 'CALISAN';
}

function UserBadge({ user, onNavigate }: { user: SidebarUser; onNavigate?: () => void }) {
  return (
    <div className="mb-4 flex items-center justify-between gap-2 rounded border border-slate-200 bg-white px-3 py-2">
      <div className="min-w-0">
        <div className="truncate text-sm font-medium text-slate-800">{user.fullName || user.username}</div>
        {user.role === 'YONETICI' && <div className="text-xs text-slate-400">Yönetici</div>}
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <Link
          href="/profile"
          onClick={onNavigate}
          className="text-xs font-medium text-slate-500 hover:text-slate-800 hover:underline"
        >
          Şifremi Değiştir
        </Link>
        <form action={logoutAction}>
          <button type="submit" className="text-xs font-medium text-slate-500 hover:text-slate-800 hover:underline">
            Çıkış
          </button>
        </form>
      </div>
    </div>
  );
}

function normalize(value: string): string {
  return value.toLocaleLowerCase('tr-TR');
}

function NavLink({ href, label, isActive, onNavigate, indent }: { href: string; label: string; isActive: boolean; onNavigate?: () => void; indent?: boolean }) {
  return (
    <Link
      href={href}
      onClick={onNavigate}
      className={`flex items-center gap-2 rounded px-2 py-1.5 text-sm ${indent ? 'pl-4 text-[13px]' : ''} ${
        isActive ? 'bg-slate-200 font-semibold text-slate-900' : 'font-medium text-slate-700 hover:bg-slate-200'
      }`}
    >
      {isActive && <span className="h-3.5 w-0.5 shrink-0 rounded-full bg-slate-900" />}
      <span className="truncate">{label}</span>
    </Link>
  );
}

function isPathActive(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}

function NavLinks({ onNavigate, role }: { onNavigate?: () => void; role: SidebarUser['role'] }) {
  const pathname = usePathname();
  const [query, setQuery] = useState('');
  const [lookupsOpen, setLookupsOpen] = useState(false);

  const quickAccess = quickAccessResources();
  const mainGroups = groupedMainResources();
  const lookupGroups = groupedLookupResources();

  const q = normalize(query.trim());
  const matches = (label: string) => q === '' || normalize(label).includes(q);

  const filteredQuickAccess = quickAccess.filter((item) => matches(item.label));
  const filteredMainGroups = mainGroups
    .map((g) => ({ group: g.group, items: g.items.filter((item) => matches(item.title)) }))
    .filter((g) => g.items.length > 0);
  const filteredLookupGroups = lookupGroups
    .map((g) => ({ group: g.group, items: g.items.filter((item) => matches(item.title)) }))
    .filter((g) => g.items.length > 0);

  // Arama bir tanım tablosuyla eşleşiyorsa, akordeon kapalıyken sonucun
  // görünmez kalmaması için otomatik açılır.
  const shouldShowLookups = lookupsOpen || (q !== '' && filteredLookupGroups.length > 0);

  return (
    <div className="space-y-5">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Menüde ara..."
        className="w-full rounded border border-slate-300 bg-white px-2.5 py-1.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none"
      />

      {filteredQuickAccess.length > 0 && (
        <div className="border-b border-slate-200 pb-5">
          <div className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">Hızlı Erişim</div>
          <ul className="space-y-0.5">
            {filteredQuickAccess.map((item) => (
              <li key={item.href}>
                <NavLink href={item.href} label={item.label} isActive={isPathActive(pathname, item.href)} onNavigate={onNavigate} />
              </li>
            ))}
          </ul>
        </div>
      )}

      {role === 'YONETICI' && matches('Kullanıcılar Büyüme Değerleme Çıpaları Yönetim') && (
        <div className="border-b border-slate-200 pb-5">
          <div className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">Yönetim</div>
          <ul className="space-y-0.5">
            {matches('Kullanıcılar') && (
              <li>
                <NavLink href="/users" label="Kullanıcılar" isActive={isPathActive(pathname, '/users')} onNavigate={onNavigate} />
              </li>
            )}
            {matches('Büyüme Değerleme Çıpaları') && (
              <li>
                <NavLink
                  href="/growth-valuation-checkpoints"
                  label="Büyüme Değerleme Çıpaları"
                  isActive={isPathActive(pathname, '/growth-valuation-checkpoints')}
                  onNavigate={onNavigate}
                />
              </li>
            )}
          </ul>
        </div>
      )}

      {filteredMainGroups.length > 0 && (
        <div className="border-b border-slate-200 pb-5">
          <div className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">Ana Kayıtlar</div>
          <ul className="space-y-3">
            {filteredMainGroups.map((group) => (
              <li key={group.group}>
                <div className="mb-1 text-[11px] font-medium text-slate-400">{group.group}</div>
                <ul className="space-y-0.5">
                  {group.items.map((resource) => (
                    <li key={resource.slug}>
                      <NavLink
                        href={`/${resource.slug}`}
                        label={resource.title}
                        isActive={isPathActive(pathname, `/${resource.slug}`)}
                        onNavigate={onNavigate}
                      />
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </div>
      )}

      {filteredLookupGroups.length > 0 && (
        <div>
          <button
            type="button"
            onClick={() => setLookupsOpen((v) => !v)}
            className="mb-1.5 flex w-full items-center justify-between text-xs font-semibold uppercase tracking-wide text-slate-400 hover:text-slate-600"
          >
            <span>Tanımlar</span>
            <span className={`transition-transform ${shouldShowLookups ? 'rotate-180' : ''}`}>▾</span>
          </button>
          {shouldShowLookups && (
            <ul className="space-y-3">
              {filteredLookupGroups.map((group) => (
                <li key={group.group}>
                  <div className="mb-1 text-[11px] font-medium text-slate-400">{group.group}</div>
                  <ul className="space-y-0.5">
                    {group.items.map((resource) => (
                      <li key={resource.slug}>
                        <NavLink
                          href={`/${resource.slug}`}
                          label={resource.title}
                          isActive={isPathActive(pathname, `/${resource.slug}`)}
                          onNavigate={onNavigate}
                          indent
                        />
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {q !== '' && filteredQuickAccess.length === 0 && filteredMainGroups.length === 0 && filteredLookupGroups.length === 0 && (
        <p className="px-2 text-sm text-slate-400">Sonuç bulunamadı.</p>
      )}
    </div>
  );
}

export function Sidebar({ user }: { user: SidebarUser }) {
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
      <header className="sticky top-0 z-30 flex h-14 shrink-0 items-center gap-3 border-b border-slate-200 bg-white px-4 lg:hidden print:hidden">
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
          className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden print:hidden"
          onClick={() => setOpen(false)}
          aria-hidden
        />
      )}

      {/* Mobil çekmece menü */}
      <nav
        className={`fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] transform overflow-y-auto border-r border-slate-200 bg-slate-50 p-4 transition-transform duration-200 ease-in-out lg:hidden print:hidden ${
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
        <UserBadge user={user} onNavigate={() => setOpen(false)} />
        <NavLinks onNavigate={() => setOpen(false)} role={user.role} />
      </nav>

      {/* Masaüstü sabit kenar çubuğu */}
      <nav className="hidden w-64 shrink-0 border-r border-slate-200 bg-slate-50 p-4 lg:block print:hidden">
        <Link href="/" className="mb-6 block text-lg font-semibold text-slate-900">
          İşletme Yönetim
        </Link>
        <UserBadge user={user} />
        <NavLinks role={user.role} />
      </nav>
    </>
  );
}
