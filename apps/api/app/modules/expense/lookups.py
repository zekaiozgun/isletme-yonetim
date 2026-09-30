"""Master Data (lookup) tables for the Expense bounded context."""

from app.core.database import Base
from app.core.orm import LookupMixin


class ExpenseCategory(LookupMixin, Base):
    """Genel işletme gideri kategorisi (Yakıt, İşçilik/Yevmiye, Usta/Bakım-
    Onarım, Diğer) - hayvana bağlı olmayan (Yem/Sağlık modüllerinin dışında
    kalan) işletme giderleri için."""

    __tablename__ = "expense_categories"
