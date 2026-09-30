"""Genel işletme giderleri (yakıt, işçilik/yevmiye, usta/bakım-onarım, diğer)

Hayvana bağlı olmayan (Yem/Sağlık modüllerinin dışında kalan) işletme
giderlerini kaydetmek için yeni bir lookup (expense_categories) + veri
tablosu (general_expenses).

Revision ID: 0030
Revises: 0029
Create Date: 2026-09-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0030"
down_revision: Union[str, None] = "0029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "expense_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO expense_categories (code, name, is_active) VALUES
            ('YAKIT', 'Yakıt', true),
            ('ISCILIK', 'İşçilik / Yevmiye', true),
            ('USTA_BAKIM_ONARIM', 'Usta / Bakım-Onarım', true),
            ('DIGER', 'Diğer', true)
            """
        )
    )

    op.create_table(
        "general_expenses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("expense_categories.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_general_expenses_expense_date", "general_expenses", ["expense_date"])


def downgrade() -> None:
    op.drop_index("ix_general_expenses_expense_date", table_name="general_expenses")
    op.drop_table("general_expenses")
    op.drop_table("expense_categories")
