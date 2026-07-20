// Bu deger yalnizca sunucu tarafinda (Server Component / Server Action)
// okunur - tarayicidan hicbir zaman dogrudan API'ye istek atilmaz, bu
// yuzden NEXT_PUBLIC_ on eki (build-time inline) GEREKMEZ; normal bir
// runtime env var olarak kalir (Docker imajini yeniden derlemeden
// degistirilebilir).
const API_URL = process.env.API_URL ?? 'http://localhost:3001';

export type ApiRecord = Record<string, unknown>;

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: 'no-store' });
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
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    return { error: `API'ye ulaşılamadı (${API_URL}). Backend çalışıyor mu?` };
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
