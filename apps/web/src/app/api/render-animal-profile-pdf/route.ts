import { NextRequest, NextResponse } from 'next/server';
import { API_URL, getAuthHeader } from '@/lib/api';

/**
 * Tarayıcı hiçbir zaman API'ye doğrudan istek atmaz (bkz. lib/api.ts) -
 * bu route, AnimalProfilePdfButton'ın client-side POST isteğini, httpOnly
 * cookie'deki JWT ile birlikte backend'in /pdf-export/animal-profile uç
 * noktasına vekaleten iletir ve dönen PDF baytlarını tarayıcıya aktarır.
 * /api/render-pdf ile AYNI desen, sadece backend hedefi farklı (bkz. o
 * dosyanın açıklaması).
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  const body = await request.text();
  const authHeader = await getAuthHeader();

  let response: Response;
  try {
    response = await fetch(`${API_URL}/pdf-export/animal-profile`, {
      method: 'POST',
      headers: { ...authHeader, 'Content-Type': 'application/json' },
      body,
    });
  } catch {
    return NextResponse.json({ error: 'API’ye ulaşılamadı.' }, { status: 502 });
  }

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    return NextResponse.json({ error: detail || 'PDF oluşturulamadı.' }, { status: response.status });
  }

  const pdfBytes = await response.arrayBuffer();
  return new NextResponse(pdfBytes, {
    status: 200,
    headers: { 'Content-Type': 'application/pdf' },
  });
}
