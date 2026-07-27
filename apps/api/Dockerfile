FROM python:3.13-slim

WORKDIR /app

# weasyprint (PDF export) metin sekillendirme icin Pango'ya (sistem
# kutuphanesi) ihtiyac duyar - pip kurulumu bunu saglamaz, apt ile ayrica
# kurulmasi gerekir (bkz. app/modules/pdf_export/service.py).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf2.0-0 \
    fonts-liberation shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Sadece requirements once kopyalanir ki kod degisince bagimlilik
# katmani yeniden indirilmesin (Docker layer cache).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3001

# Render gibi platformlar dinlenecek portu $PORT ile bildirir; kendi
# docker-compose.prod.yml'imizde bu degisken tanimli olmadigi icin 3001'e
# duser (mevcut yerel/VM kurulumu bozulmaz).
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed_all && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3001}"]
