"""Expense: hayvana bağlı olmayan genel işletme gideri kaydı.

Yem (FeedPurchase) ve Sağlık (HealthEvent.cost) maliyetleri kendi
modüllerinde zaten tutuluyor - bu modül SADECE onların dışında kalan
işletme giderlerini (yakıt, işçilik/yevmiye, usta/bakım-onarım, diğer)
kapsar (Anayasa m.6: aynı kavram için ikinci bir yer açılmaz, bu gerçekten
farklı bir kavram)."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.orm import TimestampMixin


class GeneralExpense(TimestampMixin, Base):
    __tablename__ = "general_expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("expense_categories.id"), nullable=False)
    # Fatura/fiş tutari fact olarak girilir (Anayasa m.4).
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    category = relationship("ExpenseCategory")
