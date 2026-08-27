'use client';

import * as Sentry from '@sentry/nextjs';
import { useEffect } from 'react';

/** (app) route grubu icindeki (giris yapmis kullanicinin gordugu tum
 * sayfalar) yakalanmamis bir hata icin ozel sinir - global-error.tsx'in
 * ciplak "Application error" ekrani yerine, Turkce ve tekrar deneme
 * secenegi sunan bir mesaj gosterir. Ozellikle gecici backend
 * hatalarinda (429/502/503, ornegin Render'in uyku/soguk baslangic
 * penceresinde) kullaniciyi tam sayfa cokmesiyle degil, kisa bir
 * mesajla karsilar - apiGet zaten bu kodlarda kendi icinde birkac kez
 * yeniden deniyor (bkz. lib/api.ts), bu sinir sadece o yeniden
 * denemeler de yetmediginde devreye girer.
 */
export default function AppError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 px-4 text-center">
      <p className="text-base font-semibold text-slate-900">Sunucuya şu anda ulaşılamıyor</p>
      <p className="max-w-md text-sm text-slate-500">
        Bu genelde kısa süreli bir kesinti veya bakım anıdır. Birkaç saniye bekleyip tekrar deneyebilirsin.
      </p>
      <button
        type="button"
        onClick={() => reset()}
        className="mt-1 rounded border border-slate-300 px-4 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        Tekrar Dene
      </button>
    </div>
  );
}
