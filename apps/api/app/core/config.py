from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    port: int = 3001
    cors_origin: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://isletme:isletme@localhost:5432/isletme_yonetim"
    # UYARI: production'da JWT_SECRET_KEY ortam degiskeni ile MUTLAKA
    # gercek, rastgele bir degerle degistirilmeli (orn. `openssl rand -hex 32`).
    # Bu varsayilan yalnizca yerel gelistirme icindir.
    jwt_secret_key: str = "dev-only-insecure-secret-change-in-production"
    jwt_expire_minutes: int = 60 * 24 * 365  # ~1 yil - kucuk, guvenilir bir ekip icin tekrar tekrar giris istenmesin

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origin.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
