'use client';

import * as Sentry from '@sentry/nextjs';
import NextError from 'next/error';
import { useEffect } from 'react';

// Diger tum error.tsx sinirlarindan kacan (root layout icindeki) bir
// render hatasi burada yakalanir - bugunku "Functions cannot be passed
// to Client Components" gibi hatalar tam bu sinifa girer. Sentry'ye
// bildirir, kullaniciya Next.js'in kendi genel hata sayfasini gosterir.
export default function GlobalError({ error }: { error: Error & { digest?: string } }) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html>
      <body>
        <NextError statusCode={0} />
      </body>
    </html>
  );
}
