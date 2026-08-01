import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: 'https://c606da6bc20f7b98d6eac1af55e55e3d@o4511835793915904.ingest.de.sentry.io/4511835931869264',
  sendDefaultPii: false,
  tracesSampleRate: 1.0,
});

export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
