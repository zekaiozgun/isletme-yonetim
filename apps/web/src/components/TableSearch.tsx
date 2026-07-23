'use client';

import { useRef, useState } from 'react';

interface TableSearchProps {
  placeholder?: string;
  emptyMessage?: string;
  children: React.ReactNode;
}

/**
 * Sunucuda render edilmiş bir tabloyu (children) saran istemci bileşeni.
 * Arama kutusu, tbody icindeki her <tr>'nin data-search attribute'unu
 * (ResourceTable/ReportTable tarafindan doldurulur) sorguyla karsilastirip
 * CSS ile gizler/gosterir - satirlar yeniden render edilmez, tablo verisi
 * ve lookup cozumlemesi sunucuda kalir.
 */
export function TableSearch({ placeholder = 'Ara...', emptyMessage = 'Aramanızla eşleşen kayıt yok.', children }: TableSearchProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState('');
  const [noMatches, setNoMatches] = useState(false);

  function applyFilter(value: string) {
    const needle = value.trim().toLocaleLowerCase('tr-TR');
    const rows = containerRef.current?.querySelectorAll<HTMLTableRowElement>('tbody tr[data-search]');
    let visibleCount = 0;
    rows?.forEach((row) => {
      const haystack = row.dataset.search ?? '';
      const match = needle === '' || haystack.includes(needle);
      row.classList.toggle('hidden', !match);
      if (match) visibleCount += 1;
    });
    setNoMatches(needle !== '' && visibleCount === 0);
  }

  return (
    <div>
      <input
        type="search"
        value={query}
        onChange={(event) => {
          setQuery(event.target.value);
          applyFilter(event.target.value);
        }}
        placeholder={placeholder}
        className="mb-3 w-full max-w-sm rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
      />
      <div ref={containerRef}>{children}</div>
      {noMatches && <p className="mt-3 text-sm text-slate-500">{emptyMessage}</p>}
    </div>
  );
}
