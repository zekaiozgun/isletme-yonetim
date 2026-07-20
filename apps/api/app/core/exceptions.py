"""Servis katmanının fırlattığı domain hataları.

Router katmanı bunları uygun HTTP durum koduna çevirir; servis katmanı
FastAPI/HTTP'den habersiz kalır (Clean Architecture).
"""


class DomainError(Exception):
    """Bir iş kuralı ihlal edildiğinde fırlatılır (orn. gecersiz durum geçişi)."""


class NotFoundError(DomainError):
    """Referans verilen kayıt bulunamadığında fırlatılır."""


class ConflictError(DomainError):
    """Bir kayıt, başka kayıtlarca referans verildiği için silinemediğinde fırlatılır (FK RESTRICT)."""
