"""User: sisteme giris yapabilen hesaplar. Kucuk, guvenilir bir ekip icin
tasarlandi - sadece iki rol (YONETICI, CALISAN), harici bir kimlik
saglayiciya (OAuth vb.) ihtiyac yok."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.orm import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # "YONETICI" | "CALISAN" - sabit iki deger, ayri bir lookup tablosu
    # gerektirmeyecek kadar basit (kullanicidan yonetilebilir olmasi gerekmiyor).
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="CALISAN", server_default="CALISAN")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
