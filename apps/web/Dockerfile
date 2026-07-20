# Build context REPO KOKU olmalidir (docker-compose.prod.yml'de
# context: . olarak ayarlandi) - pnpm workspace paketlerine (packages/ui,
# packages/shared, packages/types) erisebilmek icin. Basitlik icin tum
# workspace tek adimda kurulur (katman onbellegi optimizasyonu yok -
# kucuk bir proje icin build suresi onemli degil, dogruluk/basitlik onemli).

FROM node:22-slim AS base
RUN corepack enable

FROM base AS builder
WORKDIR /repo
COPY . .
RUN pnpm install --frozen-lockfile
RUN pnpm --filter=@isletme/web build

FROM base AS runner
WORKDIR /repo
ENV NODE_ENV=production
# Next.js'in standalone sunucusu bu ikisini otomatik okur; acik varsayilan
# vermek platformdan platforma (yerel docker-compose, Render, vb.) farkli
# $PORT/$HOSTNAME davranislarina karsi guvenli bir taban olusturur.
ENV HOSTNAME=0.0.0.0
ENV PORT=3000
COPY --from=builder /repo/apps/web/.next/standalone ./
COPY --from=builder /repo/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /repo/apps/web/public ./apps/web/public

EXPOSE 3000
CMD ["node", "apps/web/server.js"]
