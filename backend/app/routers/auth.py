import threading
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import ROLE_APRENDIZ, Invite, User
from app.schemas.auth import TokenResponse, UserLogin, UserOut, UserRegister
from app.security import create_access_token, hash_password, verify_password
from app.telegram import send_new_user_alert_sync

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> TokenResponse:
    invite = db.scalar(select(Invite).where(Invite.code == payload.invite_code))
    if invite is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Código de invitación desconocido")
    if invite.used_by_id is not None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Esa invitación ya fue consumida")
    if db.scalar(select(User).where(User.username == payload.username)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese nombre ya está inscrito en el grimorio")
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese correo ya está inscrito")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=ROLE_APRENDIZ,
        invites_left=0,
        invited_by_id=invite.created_by_id,
    )
    db.add(user)
    db.flush()
    invite.used_by_id = user.id
    invite.used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    user_count = db.scalar(select(func.count()).select_from(User)) or 0
    threading.Thread(
        target=send_new_user_alert_sync,
        args=(user.username, invite.created_by.username, user_count),
        daemon=True,
    ).start()
    return TokenResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(
        select(User).where((User.username == payload.username) | (User.email == payload.username))
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")
    return TokenResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user
