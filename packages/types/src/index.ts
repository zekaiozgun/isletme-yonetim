/**
 * @isletme/types
 *
 * Shared TypeScript types/interfaces used across web, mobile and api.
 * This package is intentionally empty of business/domain logic for now —
 * it only establishes the structure so future modules (e.g. inventory,
 * accounting, etc.) have a single place to define cross-app contracts.
 */

export type ID = string;

export interface Timestamped {
  createdAt: string;
  updatedAt: string;
}

// apps/api'nin OpenAPI semasindan uretilir (bkz. README.md) - backend bir
// alani silip/yeniden adlandirdiginda, bu tipleri kullanan kod derleme
// zamaninda kirilir. Su an hicbir yerde import edilmiyor (bilincli tercih -
// bkz. README); ihtiyac oldukca opt-in olarak kullanilabilir.
export type { paths as ApiPaths, components as ApiComponents } from './generated/api';

export {};
