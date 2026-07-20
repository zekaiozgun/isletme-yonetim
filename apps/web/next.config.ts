import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Docker imajını küçültür: sadece production'da gereken node_modules
  // dosyalarını .next/standalone altına toplar (bkz. apps/web/Dockerfile).
  output: 'standalone',
};

export default nextConfig;
