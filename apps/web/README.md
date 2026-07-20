# İşletme Yönetim — Web

Next.js (App Router) + TypeScript + Tailwind CSS.

## Development

From the **monorepo root** (recommended, so workspace packages link correctly):

```bash
pnpm dev --filter=@isletme/web
```

Or from this folder directly (after a root `pnpm install`):

```bash
pnpm dev
```

App runs at http://localhost:3000.

## Environment variables

Copy `.env.example` to `.env.local` and adjust values. Only variables prefixed
`NEXT_PUBLIC_` are exposed to the browser.

## Scripts

- `pnpm dev` — start the dev server
- `pnpm build` — production build
- `pnpm start` — run the production build
- `pnpm lint` — lint
- `pnpm type-check` — TypeScript check with no emit

## Structure

Standard Next.js App Router layout under `src/app`. Shared code lives in the
workspace packages `@isletme/ui`, `@isletme/shared`, `@isletme/types`.
