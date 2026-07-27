'use client';

import { useState } from 'react';

interface PdfColumn {
  label: string;
  width?: 'narrow' | 'wide';
}

interface PdfExportButtonProps {
  title: string;
  description?: string;
  columns: PdfColumn[];
  rows: string[][];
  /** Vurgulanacak (rowHighlight=true olan) satırların 0-tabanlı indeksleri. */
  highlightedRows?: number[];
  filename: string;
}

/**
 * Ekrandaki tabloyu (aynı başlık/sütun/satır verisi - bkz. CsvExportButton)
 * sunucu tarafında (weasyprint, A4 print CSS'imizle aynı mizanpaj) PDF'e
 * dönüştürüp indirir. Gerçek dönüşüm backend'de yapıldığından bu buton
 * /api/render-pdf üzerinden bir istek atar, bu yüzden CSV'nin aksine
 * asenkron bir "Hazırlanıyor…" durumu vardır.
 */
export function PdfExportButton({ title, description, columns, rows, highlightedRows, filename }: PdfExportButtonProps) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setPending(true);
    setError(null);
    try {
      const res = await fetch('/api/render-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description, columns, rows, highlighted_rows: highlightedRows ?? [] }),
      });
      if (!res.ok) {
        setError('PDF oluşturulamadı.');
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch {
      setError('PDF oluşturulamadı.');
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={handleClick}
        disabled={pending}
        className="rounded border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
      >
        {pending ? 'Hazırlanıyor…' : 'PDF olarak indir'}
      </button>
      {error && <span className="text-sm text-red-600">{error}</span>}
    </div>
  );
}
