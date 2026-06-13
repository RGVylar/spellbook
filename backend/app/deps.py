from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.artifact import STATUS_SELLADO, Artifact
from app.models.user import ROLE_APRENDIZ, ROLE_MAGO, User
from app.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _maybe_promote(user: User, db: Session) -> None:
    """Ascenso perezoso aprendiz → mago: días de antigüedad + propuestas aprobadas."""
    if user.role != ROLE_APRENDIZ:
        return
    created = user.created_at
    if created is None:
        return
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - created < timedelta(days=settings.mago_days):
        return
    approved = db.scalar(
        select(func.count())
        .select_from(Artifact)
        .where(Artifact.created_by_id == user.id, Artifact.status == STATUS_SELLADO)
    ) or 0
    if approved < settings.mago_min_approved:
        return
    user.role = ROLE_MAGO
    user.invites_left = settings.mago_invites
    db.commit()
    db.refresh(user)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    sub = decode_token(token)
    if sub is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    user = db.get(User, int(sub))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    _maybe_promote(user, db)
    return user


def get_optional_user(
    token: str | None = Depends(oauth2_optional),
    db: Session = Depends(get_db),
) -> User | None:
    if not token:
        return None
    sub = decode_token(token)
    if sub is None:
        return None
    user = db.get(User, int(sub))
    if user is not None:
        _maybe_promote(user, db)
    return user


def get_moderator_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_moderator:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo magos y el Archimago pueden moderar")
    return user


def get_archimago_user(user: User = Depends(get_current_user)) -> User:
    if user.role != "archimago":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo el Archimago puede hacer esto")
    return user
