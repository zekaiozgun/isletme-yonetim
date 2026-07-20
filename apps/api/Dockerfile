FROM python:3.13-slim

WORKDIR /app

# Sadece requirements once kopyalanir ki kod degisince bagimlilik
# katmani yeniden indirilmesin (Docker layer cache).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3001

# Render gibi platformlar dinlenecek portu $PORT ile bildirir; kendi
# docker-compose.prod.yml'imizde bu degisken tanimli olmadigi icin 3001'e
# duser (mevcut yerel/VM kurulumu bozulmaz).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3001}"]
