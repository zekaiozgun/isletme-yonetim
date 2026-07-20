"""Pen (padok) master table and animal-pen assignment history.

pen_assignments append-only bir event tablosudur (Anayasa m.8): bir hayvanin
guncel konumu, removed_date'i NULL olan satirdir. Gecmis kayitlar silinmez.
"""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class Pen(TimestampMixin, Base):
    __tablename__ = "pens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    pen_type_id: Mapped[int] = mapped_column(ForeignKey("pen_types.id"), nullable=False)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    pen_type = relationship("PenType")


class PenAssignment(TimestampMixin, Base):
    __tablename__ = "pen_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    animal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, index=True)
    pen_id: Mapped[int] = mapped_column(ForeignKey("pens.id"), nullable=False, index=True)
    assigned_date: Mapped[date] = mapped_column(Date, nullable=False)
    removed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reason_id: Mapped[int] = mapped_column(ForeignKey("pen_assignment_reasons.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    animal = relationship("Animal")
    pen = relationship("Pen")
    reason = relationship("PenAssignmentReason")
