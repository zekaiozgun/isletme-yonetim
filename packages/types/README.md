# @isletme/types

Shared TypeScript types/interfaces used as contracts between `apps/web`,
`apps/mobile`, and `apps/api`. No runtime code — types only.

## `src/generated/api.ts` — backend OpenAPI şeması

`ApiPaths`/`ApiComponents` (bu paketten export edilir) FastAPI'nin
otomatik OpenAPI şemasından üretilir — backend'de bir Pydantic alanı
silinir/yeniden adlandırılırsa, bu tipleri kullanan frontend kodu derleme
zamanında kırılır.

Yeniden üretmek için (apps/api'de bir şema değişikliği yaptıktan sonra):

```bash
cd apps/api && python scripts/export_openapi.py   # -> packages/types/openapi.json (gitignore'da, ara dosya)
cd ../../packages/types && pnpm generate:api-types # -> src/generated/api.ts (COMMIT edilir)
```

`.github/workflows/type-drift-check.yml` her push'ta bu iki adımı
çalıştırıp `src/generated/api.ts`'i yeniden üretir ve commit'lenmiş
sürümle karşılaştırır — biri unutulursa CI kırılır.

Şu an hiçbir yerde import edilmiyor (bilinçli, kademeli tercih — `resources.ts`/
`reports.ts` sütun tanımları hâlâ string-key'li genel bir yapı kullanıyor,
bkz. proje hafızasındaki Faz 4 kaydı). İhtiyaç oldukça opt-in olarak
kullanılabilir: `import type { ApiComponents } from '@isletme/types'`.
