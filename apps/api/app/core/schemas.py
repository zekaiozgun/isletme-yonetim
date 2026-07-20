"""Modüller arası paylaşılan (generic) Pydantic şemaları."""

from pydantic import BaseModel, ConfigDict


class LookupCreate(BaseModel):
    """Her Master Data / lookup tablosunun ortak veri girişi şekli."""

    code: str
    name: str
    is_active: bool = True


class LookupRead(BaseModel):
    """Her Master Data / lookup tablosunun ortak okuma şekli."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    is_active: bool
