from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth import service
from app.modules.auth.models import User
from app.modules.auth.security import decode_access_token


def extract_bearer_token(request: Request) -> str | None:
    header = request.headers.get("Authorization")
    if not header or not header.lower().startswith("bearer "):
        return None
    return header[7:].strip()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = extract_bearer_token(request)
    if token is None:
        raise HTTPException(status_code=401, detail="Giriş yapmanız gerekiyor.")

    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Oturum geçersiz veya süresi dolmuş, tekrar giriş yapın.")

    user = service.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı veya devre dışı bırakılmış.")

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "YONETICI":
        raise HTTPException(status_code=403, detail="Bu işlem için yönetici yetkisi gerekiyor.")
    return user
