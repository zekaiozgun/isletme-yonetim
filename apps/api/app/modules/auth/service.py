from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate
from app.modules.auth.security import hash_password, verify_password


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.scalars(select(User).where(User.username == username)).first()
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.username)).all())


def any_user_exists(db: Session) -> bool:
    return db.scalars(select(User.id).limit(1)).first() is not None


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(f"'{data.username}' kullanıcı adı zaten kayıtlı.") from exc
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"Kullanıcı bulunamadı: {user_id}")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def activate_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"Kullanıcı bulunamadı: {user_id}")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


def change_own_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    """Mevcut sifre eslesmezse False doner (router 400'e cevirir) - login'deki
    authenticate_user ile ayni desen: gecersizlik burada degil router'da HTTP
    hatasina cevrilir."""
    if not verify_password(current_password, user.password_hash):
        return False
    user.password_hash = hash_password(new_password)
    db.commit()
    return True


def reset_user_password(db: Session, user_id: int, new_password: str) -> User:
    """YONETICI'nin baska bir kullanicinin sifresini mevcut sifreyi bilmeden
    sifirlamasi - unutulan sifre senaryosu."""
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"Kullanıcı bulunamadı: {user_id}")
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user
