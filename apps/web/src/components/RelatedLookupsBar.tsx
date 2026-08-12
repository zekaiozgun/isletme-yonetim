/** Bir veri giriş formunun üstünde, o formu doldurmadan önce dolu olması
 * gereken tanım/referans kayıtlarına (bkz. lib/resources.ts
 * getRelatedLookups) hızlı link verir - kullanıcı "bu bilgiyi nereden
 * bulacağım/oluşturacağım" diye vakit kaybetmesin diye. Yeni sekmede açılır
 * (target="_blank") - aksi halde doldurmakta olduğu form verisini kaybeder. */
export function RelatedLookupsBar({ items }: { items: { slug: string; title: string }[] }) {
  if (items.length === 0) return null;

  return (
    <p className="mb-4 text-sm text-slate-500">
      Tanım eksikse:{' '}
      {items.map((item, index) => (
        <span key={item.slug}>
          {index > 0 && ' · '}
          <a
            href={`/${item.slug}`}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-slate-700 hover:underline"
          >
            {item.title} ↗
          </a>
        </span>
      ))}
    </p>
  );
}
