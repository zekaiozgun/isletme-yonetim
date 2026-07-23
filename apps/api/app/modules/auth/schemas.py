from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Role = Literal["YONETICI", "CALISAN"]


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    role: Role = "CALISAN"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str | None = None
    role: Role
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    """Kullanıcının kendi şifresini değiştirmesi - mevcut şifre dogrulanir."""

    current_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    """YONETICI'nin baska bir kullanicinin sifresini sifirlamasi - mevcut
    sifre bilgisi istenmez (unutulan sifre senaryosu icindir)."""

    new_password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
