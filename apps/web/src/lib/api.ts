import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

// Bu deger yalnizca sunucu tarafinda (Server Component / Server Action)
// okunur - tarayicidan hicbir zaman dogrudan API'ye istek atilmaz, bu
// yuzden NEXT_PUBLIC_ on eki (build-time inline) GEREKMEZ; normal bir
// runtime env var olarak kalir (Docker imajini yeniden derlemeden
// degistirilebilir).
const API_URL = process.env.API_URL ?? 'http://localhost:3001';

// httpOnly cookie'de tutulan JWT - tarayici bu cookie'yi API'ye hicbir zaman
// dogrudan gondermez, sadece Next.js sunucusu (asagidaki getAuthHeader)
// istekleri API'ye vekaleten yaparken Authorization header'ina ekler.
export const AUTH_COOKIE_NAME = 'isletme_token';

export type ApiRecord = Record<string, unknown>;

async function getAuthHeader(): Promise<Record<string, string>> {
  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiGet<T>(path: string): Promise<T> {
  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_URL}${path}`, { cache: 'no-store', headers: authHeader });
  if (res.status === 401) {
    redirect('/login');
  }
  if (!res.ok) {
    throw new Error(`API isteği başarısız oldu: ${path} (${res.status})`);
  }
  return (await res.json()) as T;
}

/** Bir GET isteği başarısız olursa (örn. henüz seed edilmemiş bir lookup) çökmek yerine boş liste döner. */
export async function apiGetSafe<T>(path: string, fallback: T): Promise<T> {
  try {
    return await apiGet<T>(path);
  } catch {
    return fallback;
  }
}

type ApiResult<T> = { data: T; error?: undefined } | { data?: undefined; error: string };

async function apiSend<T>(
  method: 'POST' | 'PUT' | 'DELETE',
  path: string,
  body?: Record<string, unknown>
): Promise<ApiResult<T>> {
  const authHeader = await getAuthHeader();
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers: { ...authHeader, ...(body ? { 'Content-Type': 'application/json' } : {}) },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    return { error: `API'ye ulaşılamadı (${API_URL}). Backend çalışıyor mu?` };
  }

  // /auth/login'in kendisi haric: oradaki 401 "sifre yanlis" gibi normal bir
  // is hatasidir (login formunda gosterilmeli), oturum suresi dolmasi degil.
  if (res.status === 401 && path !== '/auth/login') {
    redirect('/login');
  }

  if (!res.ok) {
    const errorBody: unknown = await res.json().catch(() => null);
    return { error: extractErrorMessage(errorBody) ?? `İstek başarısız oldu (${res.status})` };
  }

  if (res.status === 204) {
    return { data: undefined as T };
  }
  return { data: (await res.json()) as T };
}

export function apiPost<T>(path: string, body: Record<string, unknown>): Promise<ApiResult<T>> {
  return apiSend<T>('POST', path, body);
}

export function apiPut<T>(path: string, body: Record<string, unknown>): Promise<ApiResult<T>> {
  return apiSend<T>('PUT', path, body);
}

export function apiDelete(path: string): Promise<ApiResult<undefined>> {
  return apiSend<undefined>('DELETE', path);
}

function extractErrorMessage(body: unknown): string | null {
  if (!body || typeof body !== 'object') return null;
  const detail = (body as { detail?: unknown }).detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === 'object' && 'msg' in item) {
          const loc = 'loc' in item && Array.isArray((item as { loc?: unknown[] }).loc) ? (item as { loc: unknown[] }).loc.join('.') : '';
          return `${loc ? loc + ': ' : ''}${String((item as { msg: unknown }).msg)}`;
        }
        return JSON.stringify(item);
      })
      .join('; ');
  }
  return null;
}
