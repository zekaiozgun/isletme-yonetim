# İşletme Yönetim

Beef Cattle Management System — bkz. [`PROJECT SCOPE.txt`](./PROJECT%20SCOPE.txt)
icin V1 kapsami ve mimari kurallar (DDD, Clean Architecture).

> **Durum:** V1 kapsamindaki tum modullerin veritabani semasi (tablolar +
> migration'lar + master data) tamamlandi: Animal, Pen, Genetic Resource,
> Weight, Breeding, Health, Feed, Sale, Death. Dashboard tablo gerektirmez
> (salt okunur raporlama). Sirada: auth, servis katmani (hesaplamalar,
> Animal.status senkronu) ve CRUD API endpoint'leri.

## Tech stack

- **Monorepo:** Turborepo + pnpm workspaces (yalnizca web + mobile icin)
- **Web:** Next.js (App Router) + TypeScript + Tailwind CSS
- **Mobile:** React Native + Expo + TypeScript
- **Backend:** Python + FastAPI + SQLAlchemy + Alembic — pnpm/turbo
  workspace'inin **disindadir**, ayri calistirilir (bkz.
  [`apps/api/README.md`](./apps/api/README.md))
- **Veritabani:** PostgreSQL (lokal gelistirme icin `docker-compose.yml`)
- **Shared:** internal packages for types, utilities, and UI components

## Folder structure

```
isletme-yonetim/
├── apps/
│   ├── web/          Next.js app (@isletme/web)
│   ├── mobile/        Expo app (@isletme/mobile)
│   └── api/            FastAPI app (Python — pnpm workspace'inde degil)
├── packages/
│   ├── ui/             Shared React components (@isletme/ui)
│   ├── shared/         Shared framework-agnostic utilities (@isletme/shared)
│   └── types/          Shared TypeScript types (@isletme/types)
├── docker-compose.yml    Lokal PostgreSQL
├── package.json         Root scripts (turbo pipelines, web+mobile icin)
├── pnpm-workspace.yaml   Workspace package globs
├── turbo.json            Turborepo pipeline config
├── tsconfig.base.json     Shared TypeScript compiler options
├── eslint.config.mjs      Shared ESLint (flat) config
└── .prettierrc.json       Shared Prettier config
```

Each app and package has its own `README.md` with app-specific notes.

## Prerequisites

- Node.js ≥ 20
- pnpm ≥ 9 (repo pins `packageManager: pnpm@10.28.0`; enable via `corepack enable`)
- Python ≥ 3.11 (backend icin — bkz. [`apps/api/README.md`](./apps/api/README.md))
- Docker (lokal PostgreSQL icin)
- For mobile native builds: Expo Go app (or Xcode / Android Studio for
  simulators) — not required just to start the dev server

## Installation

```bash
# from the repo root
corepack enable          # ensures the pinned pnpm version is used
pnpm install              # web + mobile + shared packages
docker compose up -d postgres
```

Backend kurulumu icin [`apps/api/README.md`](./apps/api/README.md) dosyasina bakin
(Python sanal ortami, `pip install`, `alembic upgrade head`).

This installs dependencies for every JS/TS app/package and links the
internal `@isletme/*` workspace packages together. `apps/api` bu adima
dahil degildir — kendi Python ortamiyla ayri kurulur.

## Environment variables

Each app has its own `.env.example`. Copy it and fill in values:

```bash
cp apps/web/.env.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
cp apps/mobile/.env.example apps/mobile/.env
```

Real `.env*` files are git-ignored; only `.env.example` files are committed.

## Running everything

Web + mobile (Turborepo):

```bash
pnpm dev
```

Run a single JS/TS app:

```bash
pnpm dev --filter=@isletme/web       # http://localhost:3000
pnpm dev --filter=@isletme/mobile    # Expo dev tools
```

Backend (ayri terminal, `apps/api` icinden — detay icin apps/api/README.md):

```bash
uvicorn app.main:app --reload --port 3001
```

## Other common commands

```bash
pnpm build          # build web + mobile (turbo run build)
pnpm lint           # lint web + mobile + packages
pnpm type-check      # TypeScript check across web + mobile + packages
pnpm format          # format with Prettier
pnpm format:check    # check formatting without writing
```

## TypeScript

`tsconfig.base.json` at the root defines shared compiler options and path
aliases for the internal packages (`@isletme/ui`, `@isletme/shared`,
`@isletme/types`). Each app has its own `tsconfig.json` that extends or
composes with these settings. (`apps/api` bir Python projesi oldugu icin
bu TypeScript yapilandirmasina dahil degildir.)

## Linting & formatting

- ESLint: a shared flat config (`eslint.config.mjs`) at the root; `apps/web`
  layers in `eslint-config-next`, `apps/mobile` layers in
  `eslint-config-expo`. `apps/api` (Python) `ruff` kullanir — bkz.
  `apps/api/requirements-dev.txt`.
- Prettier: a single shared `.prettierrc.json` for the whole (JS/TS) repo.

## Remaining setup notes

- **Native mobile builds** (EAS Build, app store credentials, push
  notification certs) are not configured — only the Expo dev workflow is
  ready out of the box.
- **CI/CD** is not set up yet (no GitHub Actions/workflows included).
- **Auth ve diger domain moduller** (Weight, Breeding, Health, Feed, Pen,
  Sale, Death, Dashboard) henuz implemente edilmedi — her biri ayri bir
  takip gorevi olarak eklenecek.
- The `@isletme/ui` package targets web/DOM (plain React); if/when mobile
  needs shared UI primitives, introduce a cross-platform layer (e.g.
  react-native-web) rather than assuming direct reuse.
- Root `packageManager` is pinned to `pnpm@10.28.0` — run `corepack enable`
  once per machine so pnpm resolves to the same version everyone else uses.
