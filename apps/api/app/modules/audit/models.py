"""Audit log: her CREATE/UPDATE/DELETE'i kim/ne-zaman/hangi-kayit bilgisiyle
otomatik olarak yakalar (bkz. app/core/audit.py'deki mapper-seviyesi
SQLAlchemy event listener'lari) - hicbir servis fonksiyonu elle audit
kaydi yazmaz. Immutable oldugu icin updated_at yok, TimestampMixin
kullanilmiyor."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(16), nullable=False)  # CREATE | UPDATE | DELETE
    table_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    record_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    user = relationship("User")

    @property
    def username(self) -> str | None:
        return self.user.username if self.user else None
