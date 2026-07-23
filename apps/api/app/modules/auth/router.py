from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ConflictError
from app.modules.auth import service
from app.modules.auth.dependencies import get_current_user, require_admin
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
    UserCreate,
    UserRead,
)
from app.modules.auth.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = service.authenticate_user(db, payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı.")
    token = create_access_token(user.id)
    return LoginResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/bootstrap", response_model=UserRead, status_code=201)
def bootstrap_first_admin(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    """Girissiz erisilebilir TEK istisna - ama yalnizca sistemde HENUZ HICBIR
    kullanici yokken calisir (ilk yonetici hesabini olusturmak icin). Ilk
    kullanici olusturulduktan sonra bu uc nokta kalici olarak 409 doner,
    bir daha asla kullanilamaz - guvenlik acigi penceresi bu ilk andir."""
    if service.any_user_exists(db):
        raise HTTPException(status_code=409, detail="Sistemde zaten kullanıcı var, bootstrap kapalı.")
    data = payload.model_copy(update={"role": "YONETICI"})
    return service.create_user(db, data)


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)


@router.get("/users", response_model=list[UserRead], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return service.list_users(db)


@router.post("/users", response_model=UserRead, status_code=201, dependencies=[Depends(require_admin)])
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    try:
        return service.create_user(db, payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/users/{user_id}", response_model=UserRead, dependencies=[Depends(require_admin)])
def deactivate_user(user_id: int, db: Session = Depends(get_db)) -> User:
    return service.deactivate_user(db, user_id)


@router.post("/users/{user_id}/activate", response_model=UserRead, dependencies=[Depends(require_admin)])
def activate_user(user_id: int, db: Session = Depends(get_db)) -> User:
    return service.activate_user(db, user_id)


@router.post("/me/change-password", response_model=UserRead)
def change_own_password(
    payload: ChangePasswordRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> User:
    ok = service.change_own_password(db, user, payload.current_password, payload.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="Mevcut şifre hatalı.")
    return user


@router.post("/users/{user_id}/reset-password", response_model=UserRead, dependencies=[Depends(require_admin)])
def reset_user_password(user_id: int, payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> User:
    return service.reset_user_password(db, user_id, payload.new_password)
