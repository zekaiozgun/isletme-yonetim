"""API'nin OpenAPI semasini JSON dosyasina yazar - hicbir veritabani
baglantisi gerektirmez (app.openapi() salt route/pydantic sema
introspeksiyonu yapar). packages/types'daki openapi-typescript adimi
bu ciktiyi girdi olarak kullanir.

Kullanim: python scripts/export_openapi.py [cikti-yolu]
(apps/api dizininden calistirilmalidir; varsayilan cikti yolu
../../packages/types/openapi.json)

Dosyaya dogrudan UTF-8 ile yazilir (stdout'a yazip yonlendirmek Windows'ta
konsol kod sayfasi Turkce karakterleri encode edemedigi icin patlar).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402 - once sys.path duzeltilmeden import edilemez

DEFAULT_OUTPUT = Path(__file__).resolve().parents[3] / "packages" / "types" / "openapi.json"


def main() -> None:
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output_path.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OpenAPI semasi yazildi: {output_path}")


if __name__ == "__main__":
    main()
