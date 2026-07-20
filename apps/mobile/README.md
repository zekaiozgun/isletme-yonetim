# İşletme Yönetim — Mobile

Expo (React Native) + TypeScript.

## Development

From the **monorepo root** (recommended):

```bash
pnpm dev --filter=@isletme/mobile
```

Or from this folder directly (after a root `pnpm install`):

```bash
pnpm start
```

This opens the Expo dev tools; scan the QR code with the Expo Go app, or press
`a` / `i` / `w` to open Android / iOS / web.

## Environment variables

Copy `.env.example` to `.env` and adjust values. Only variables prefixed
`EXPO_PUBLIC_` are exposed to app code.

## Scripts

- `pnpm start` — start the Expo dev server
- `pnpm android` / `pnpm ios` / `pnpm web` — start targeting a platform
- `pnpm lint` — lint
- `pnpm type-check` — TypeScript check with no emit

## Structure

Entry point is `index.ts` → `App.tsx`. Shared code lives in the workspace
packages `@isletme/shared`, `@isletme/types` (UI primitives in `@isletme/ui`
target web/DOM and are not used here — a cross-platform component layer can
be introduced later if needed, e.g. via react-native-web).
