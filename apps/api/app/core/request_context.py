"""İstek boyunca geçerli olan, o an giriş yapmış kullanıcının id'sini taşır.

Audit log (app/core/audit.py), her DB değişikliğinde "kim yaptı" bilgisini
servis fonksiyonlarının imzasını değiştirmeden buradan okur - auth
dependency'si (app/modules/auth/dependencies.py) istek başında bunu set eder.
"""

from contextvars import ContextVar

current_user_id: ContextVar[int | None] = ContextVar("current_user_id", default=None)
