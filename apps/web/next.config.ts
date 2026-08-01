import type { NextConfig } from 'next';
import { withSentryConfig } from '@sentry/nextjs';

const nextConfig: NextConfig = {
  // Docker imajını küçültür: sadece production'da gereken node_modules
  // dosyalarını .next/standalone altına toplar (bkz. apps/web/Dockerfile).
  output: 'standalone',
};

// SENTRY_AUTH_TOKEN yoksa (bu projede yok - ekstra gizli anahtar
// eklemekten kaçınıldı), kaynak harita (source map) yüklemesi sessizce
// atlanır - build başarısız olmaz, sadece Sentry panelindeki stack
// trace'ler minified (küçültülmüş) görünür.
export default withSentryConfig(nextConfig, {
  silent: true,
});
