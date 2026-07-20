"""Sale: alici master verisi ve satis olay kaydi.

sales.animal_id unique'tir: V1'de bir hayvan bir kez satilir (satildiktan
sonra isletme envanterinden cikar). Animal.status_id/status_date, bu
kaydin olusturulmasiyla servis katmani tarafindan senkronize edilecektir
(Anayasa m.8) - bu gorevin kapsami disinda.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class Buyer(TimestampMixin, Base):
    __tablename__ = "buyers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tax_no: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Sale(TimestampMixin, Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    animal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, unique=True
    )
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("buyers.id"), nullable=False)
    sale_type_id: Mapped[int] = mapped_column(ForeignKey("sale_types.id"), nullable=False)
    sale_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    animal = relationship("Animal")
    buyer = relationship("Buyer")
    sale_type = relationship("SaleType")
