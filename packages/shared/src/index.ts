/**
 * @isletme/shared
 *
 * Shared, framework-agnostic utilities used by web, mobile and api.
 * Kept minimal on purpose — this is scaffolding, not business logic.
 */

export const APP_NAME = 'İşletme Yönetim';

export function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}
