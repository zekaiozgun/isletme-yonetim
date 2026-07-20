"""Death: olum olay kaydi.

deaths.animal_id unique'tir (bir hayvan bir kez olur). Animal.status_id/
status_date/death_reason_id, bu kaydin olusturulmasiyla servis katmani
tarafindan senkronize edilecektir (Anayasa m.8) - bu gorevin kapsami
disinda.
"""

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class Death(TimestampMixin, Base):
    __tablename__ = "deaths"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    animal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, unique=True
    )
    death_date: Mapped[date] = mapped_column(Date, nullable=False)
    death_reason_id: Mapped[int] = mapped_column(ForeignKey("death_reasons.id"), nullable=False)
    disposal_method_id: Mapped[int] = mapped_column(ForeignKey("disposal_methods.id"), nullable=False)
    necropsy_performed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    animal = relationship("Animal")
    death_reason = relationship("DeathReason")
    disposal_method = relationship("DisposalMethod")
