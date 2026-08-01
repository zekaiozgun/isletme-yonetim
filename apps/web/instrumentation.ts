import * as Sentry from '@sentry/nextjs';

const dsn = 'https://c606da6bc20f7b98d6eac1af55e55e3d@o4511835793915904.ingest.de.sentry.io/4511835931869264';

export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    Sentry.init({ dsn, sendDefaultPii: false, tracesSampleRate: 1.0 });
  }
  if (process.env.NEXT_RUNTIME === 'edge') {
    Sentry.init({ dsn, sendDefaultPii: false, tracesSampleRate: 1.0 });
  }
}

export const onRequestError = Sentry.captureRequestError;
