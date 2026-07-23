'use client';

interface CsvExportButtonProps {
  headers: string[];
  rows: string[][];
  filename: string;
}

// Excel (ozellikle Turkce yerel ayarlarda) ondalik ayirici olarak virgul
// kullandigindan, virgullu CSV'yi tek sutuna yiginlar - noktali virgul (;)
// ayirici bu sorunu yasamaz. UTF-8 BOM olmadan Excel dogrudan actiginda
// Turkce karakterleri yanlis gosterir.
const UTF8_BOM = '﻿';

function escapeCsvField(value: string): string {
  const needsQuoting = /["\n;]/.test(value);
  const escaped = value.replace(/"/g, '""');
  return needsQuoting ? `"${escaped}"` : escaped;
}

function buildCsv(headers: string[], rows: string[][]): string {
  const lines = [headers, ...rows].map((line) => line.map(escapeCsvField).join(';'));
  return UTF8_BOM + lines.join('\r\n');
}

/** Ekrandaki tabloyu (baslik + goruntulenen ayni satirlar) analiz amacli
 * Excel/CSV'ye aktarir - fetch/API cagrisi yok, veri zaten sunucuda
 * hazirlanip prop olarak gecirilmis (bkz. ResourceTable/ReportTable). */
export function CsvExportButton({ headers, rows, filename }: CsvExportButtonProps) {
  function handleClick() {
    const csv = buildCsv(headers, rows);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className="rounded border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
    >
      CSV olarak indir
    </button>
  );
}
