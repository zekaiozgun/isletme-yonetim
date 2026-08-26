'use client';

import { useState } from 'react';

export interface PdfKeyValueBox {
  label: string;
  value: string;
  sublabel?: string;
  badge?: string;
  badgeNegative?: boolean;
}

export interface PdfSimpleTableData {
  title: string;
  columns: string[];
  rows: string[][];
}

export interface PdfWeightPointData {
  date: string;
  value: number;
}

export interface AnimalProfilePdfData {
  title: string;
  subtitle: string;
  metaLine: string;
  geneticComposition?: string | null;
  infoBoxes: PdfKeyValueBox[];
  pedigreeTable?: PdfSimpleTableData | null;
  weightPoints: PdfWeightPointData[];
  tables: PdfSimpleTableData[];
}

/**
 * Hayvan Profili sayfasının TAMAMINI (kimlik, değerleme, genetik karma,
 * soy kütüğü, kilo trend grafiği, sağlık/üreme/padok/değerlendirme
 * geçmişi) tek bir PDF belgesine dönüştürür - PdfExportButton ile AYNI
 * "sunucu tarafında (weasyprint) render et, /api/... üzerinden indir"
 * deseni, ama çok-tablolu genel amaçlı renderer yerine kendi özel
 * backend uç noktasını (POST /pdf-export/animal-profile) kullanır çünkü
 * bu belge tek bir tablo değil, birden fazla bölümden oluşuyor.
 */
export function AnimalProfilePdfButton({ data, filename }: { data: AnimalProfilePdfData; filename: string }) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setPending(true);
    setError(null);
    try {
      const res = await fetch('/api/render-animal-profile-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: data.title,
          subtitle: data.subtitle,
          meta_line: data.metaLine,
          genetic_composition: data.geneticComposition ?? null,
          info_boxes: data.infoBoxes.map((box) => ({
            label: box.label,
            value: box.value,
            sublabel: box.sublabel,
            badge: box.badge,
            badge_negative: box.badgeNegative ?? false,
          })),
          pedigree_table: data.pedigreeTable
            ? {
                title: data.pedigreeTable.title,
                columns: data.pedigreeTable.columns,
                rows: data.pedigreeTable.rows,
              }
            : null,
          weight_points: data.weightPoints,
          tables: data.tables.map((t) => ({ title: t.title, columns: t.columns, rows: t.rows })),
        }),
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
        {pending ? 'Hazırlanıyor…' : 'Profili PDF Olarak İndir'}
      </button>
      {error && <span className="text-sm text-red-600">{error}</span>}
    </div>
  );
}
