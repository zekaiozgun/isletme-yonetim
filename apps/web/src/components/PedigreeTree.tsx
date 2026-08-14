import Link from 'next/link';
import type { ApiRecord } from '@/lib/api';

/** Anne/Baba Bazında Yavru Listesi'nin tersi yönü: bir hayvanın kendi
 * ATALARI - bkz. GET /animals/{id}/pedigree, backend'de hiçbir yerde
 * saklanmaz, mother_id/father_sire_id zincirinden her istekte yeniden
 * kurulur. Sürüye ait bir ata linke tıklanabilir; dış kaynaklı (suni
 * tohumlama) bir boğada zincir o düğümde sonlanır - kendi ebeveyni
 * sistemde bilinmez (bkz. proje planı Faz 2: bilinen kimlik alanları). */
function PedigreeBranch({ label, node }: { label: string; node: ApiRecord | null }) {
  if (!node) {
    return (
      <div>
        <p className="text-xs font-medium text-slate-500">{label}</p>
        <p className="text-sm text-slate-400">—</p>
      </div>
    );
  }

  const animalId = node.animal_id ? String(node.animal_id) : null;
  const tagNumber = node.tag_number ? String(node.tag_number) : null;
  const name = node.name ? String(node.name) : null;
  const isExternal = node.is_external === true;

  const display = animalId
    ? `${tagNumber ?? '—'}${name ? ' — ' + name : ''}`
    : `${tagNumber ? tagNumber + ' — ' : ''}${name ?? '—'}${isExternal ? ' (dış kaynak)' : ''}`;

  const mother = (node.mother as ApiRecord | null) ?? null;
  const father = (node.father as ApiRecord | null) ?? null;

  return (
    <div>
      <p className="text-xs font-medium text-slate-500">{label}</p>
      {animalId ? (
        <Link href={`/animals/${animalId}/profile`} className="text-sm font-medium text-slate-800 hover:underline">
          {display}
        </Link>
      ) : (
        <p className="text-sm font-medium text-slate-800">{display}</p>
      )}
      {(mother || father) && (
        <div className="mt-1.5 space-y-1.5 border-l border-slate-200 pl-3">
          <PedigreeBranch label="Anne" node={mother} />
          <PedigreeBranch label="Baba" node={father} />
        </div>
      )}
    </div>
  );
}

export interface PedigreeTableRow {
  generation: number;
  relation: string;
  tagNumber: string;
  name: string;
  breedName: string;
  ratio: string;
}

/** Soy Kütüğü Belgesi (PDF) için - ağacı, mevcut genel amaçlı tablo PDF
 * altyapısının (bkz. components/PdfExportButton.tsx) anlayacağı düz bir
 * satır listesine çevirir. Hiçbir yeni backend uç noktası GEREKMEZ -
 * zaten fetch edilmiş ağaç, sadece farklı şekilde sunulur. Dal bazında
 * (önce anne tarafı tam, sonra baba tarafı tam) toplanır, sonra nesile
 * göre KARARLI (stable) sıralanır - böylece aynı nesildeki tüm satırlar
 * bir arada görünür ama dal içi sıra bozulmaz. */
export function flattenPedigreeTree(node: ApiRecord | null): PedigreeTableRow[] {
  const rows: PedigreeTableRow[] = [];

  function visit(current: ApiRecord | null, generation: number, relationPath: string[]): void {
    if (!current) return;
    rows.push({
      generation,
      relation: relationPath.length === 0 ? 'Kendisi' : relationPath.join(' › '),
      tagNumber: current.tag_number ? String(current.tag_number) : '—',
      name: current.name ? String(current.name) : '—',
      breedName: current.breed_name ? String(current.breed_name) : '—',
      ratio:
        current.crossbreed_ratio !== null && current.crossbreed_ratio !== undefined
          ? `%${String(current.crossbreed_ratio)}`
          : '—',
    });
    visit((current.mother as ApiRecord | null) ?? null, generation + 1, [...relationPath, 'Anne']);
    visit((current.father as ApiRecord | null) ?? null, generation + 1, [...relationPath, 'Baba']);
  }

  visit(node, 0, []);
  return rows.sort((a, b) => a.generation - b.generation);
}

export function PedigreeTree({ node }: { node: ApiRecord | null }) {
  if (!node) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <PedigreeBranch label="Anne" node={null} />
        <PedigreeBranch label="Baba" node={null} />
      </div>
    );
  }
  const mother = (node.mother as ApiRecord | null) ?? null;
  const father = (node.father as ApiRecord | null) ?? null;
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <PedigreeBranch label="Anne" node={mother} />
      <PedigreeBranch label="Baba" node={father} />
    </div>
  );
}
