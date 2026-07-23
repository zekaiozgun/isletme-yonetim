import { NextResponse, type NextRequest } from 'next/server';

const AUTH_COOKIE_NAME = 'isletme_token';

/**
 * Sadece cookie'nin VARLIGINI kontrol eder (JWT gecerliligini degil - bu,
 * edge runtime'da imza dogrulamasi gerektirir, gereksiz karmasiklik).
 * Gercek gecerlilik kontrolu API'de yapilir; token gecersiz/suresi
 * dolmussa apiGet/apiSend (lib/api.ts) zaten /login'e yonlendirir. Bu
 * middleware sadece hic cookie'si olmayan ziyaretcileri erken yakalayip
 * gereksiz bir API cagrisi yapmadan /login'e gonderir.
 */
export function middleware(request: NextRequest) {
  const token = request.cookies.get(AUTH_COOKIE_NAME)?.value;
  if (!token) {
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!login|_next/static|_next/image|favicon.ico).*)'],
};
