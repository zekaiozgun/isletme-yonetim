# @isletme/api (Python / FastAPI)

Backend, Turborepo/pnpm workspace'inin bir parcasi degildir (Python
projesidir); kendi sanal ortami ve bagimliliklariyla ayri calistirilir.

## Mimari

- **DDD + Clean Architecture** (bkz. `../../PROJECT SCOPE.txt`)
- `app/core/` — framework/altyapi: config, DB engine/session, paylasilan ORM mixin'leri
- `app/modules/<domain>/` — her bounded context kendi klasorunde, bagimsiz gelisir (Anayasa m.10)
  - `lookups.py` — Master Data (lookup) tablolari
  - `models.py` — SQLAlchemy ORM entity'leri
  - `schemas.py` — Pydantic veri sozlesmeleri (Create/Read ayrimi, Anayasa m.2)
  - `seed.py` — lookup tablolari icin baslangic referans verisi

`Animal` (`app/modules/animal/models.py`), sistemin Master Entity'sidir
(Anayasa m.7); diger tum moduller `animal_id` uzerinden buna baglanir.

## Modul haritasi (V1 kapsami tamamlandi)

| Modul | Tablolar |
| --- | --- |
| animal | breeds, genders, birth_types, litter_types, horn_statuses, source_farms, entry_sources, animal_statuses, death_reasons, **animals** |
| pen | pen_types, pen_assignment_reasons, pens, pen_assignments |
| genetic_resource | sires, semen_batches (breeds + source_farms'i yeniden kullanir) |
| weight | weighing_methods, weight_records |
| breeding | service_methods, pregnancy_check_methods, pregnancy_results, breeding_events, pregnancy_checks |
| health | health_event_types, diseases, medication_types, dosage_units, medications, health_events |
| feed | feed_types, feed_units, feed_items, feed_distributions (pens'e baglidir) |
| sale | sale_types, buyers, sales |
| death | disposal_methods, deaths (death_reasons'i animal modulunden yeniden kullanir) |
| dashboard | tablo yok — salt okunur raporlama katmani, diger modulleri sorgular |

Migration sirasi (`alembic/versions/0001`..`0009`) tam olarak bu FK
bagimlilik sirasini izler: pen ve genetic_resource, breeding ve feed'den
once gelir.

## Kurulum

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
```

## Veritabani

### Secenek A: Docker (varsa)

Repo kokunden:

```bash
docker compose up -d postgres
```

### Secenek B: Native PostgreSQL (bu makinede Docker Desktop olmadigi icin kullanildi)

PostgreSQL 17, `C:\Program Files\PostgreSQL\17` altina kuruldu ancak winget/EDB
installer Windows servisini kaydedemedi (yonetici izni gerektiriyor). Veri
dizini `C:\Users\denem\pgdata17` altinda, sunucu **pg_ctl ile elle** baslatilir
- bilgisayar yeniden baslatildiginda veya bu oturum kapandiginda **otomatik
baslamaz**:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" -D "C:\Users\denem\pgdata17" -l "C:\Users\denem\pgdata17\logfile.txt" -o "-p 5432" start
```

Durdurmak icin: `... pg_ctl.exe -D "C:\Users\denem\pgdata17" stop`

- Superuser: `postgres` / `postgres_dev_pw` (yalnizca admin islemleri icin)
- Uygulama rolu: `isletme` / `isletme` (`.env.example`'daki `DATABASE_URL` ile
  eslesir), veritabani: `isletme_yonetim` (zaten olusturuldu)
- Kalici hale getirmek isterseniz: yonetici PowerShell'den
  `& "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" register -N postgresql-x64-17 -D "C:\Users\denem\pgdata17"`
  calistirip servisi Windows Hizmetleri'nden otomatik baslamaya ayarlayabilirsiniz.

## Migration calistirma

```bash
cd apps/api
alembic upgrade head

# lookup tablolarina referans veri ekler (seed.py'si olan her modul icin)
python -m app.modules.animal.seed
python -m app.modules.pen.seed
python -m app.modules.weight.seed
python -m app.modules.breeding.seed
python -m app.modules.health.seed
python -m app.modules.feed.seed
python -m app.modules.sale.seed
python -m app.modules.death.seed
```

`genetic_resource` modulunun kendi lookup tablosu yoktur (breeds ve
source_farms'i yeniden kullanir), bu yuzden ayri bir seed script'i yoktur.

## Gelistirme sunucusu

```bash
uvicorn app.main:app --reload --port 3001
```

Saglik kontrolu: `GET http://localhost:3001/health`

## Yeni migration olusturma

Model degistirdikten sonra:

```bash
alembic revision --autogenerate -m "aciklama"
alembic upgrade head
```

## Dogrulanmis durum

Tum 9 modul, gercek bir PostgreSQL veritabanina karsi uctan uca test edildi:
migration'lar (`alembic upgrade head`), seed'ler, ve API uzerinden hayvan
olusturma → tarti/ADG hesaplama → padok atama (onceki kaydi kapatma kurali) →
saglik olayi/arinma suresi hesaplama → aşim/tahmini dogum tarihi hesaplama →
satis (Animal.status senkronu) → olum (Animal.status senkronu) akislarinin
hepsi calisiyor. Sunucu su an `http://localhost:3001` adresinde calisir
durumda birakildi; interaktif dokumantasyon icin `http://localhost:3001/docs`
adresini tarayicida acabilirsiniz.

Test sirasinda olusturulan iki ornek hayvan (TR-0001: satildi, TR-0002:
oldu) veritabaninda demo/test verisi olarak durmaktadir; temiz baslamak
isterseniz `alembic downgrade base && alembic upgrade head` ile semayi
sifirlayip seed'leri yeniden calistirabilirsiniz.
