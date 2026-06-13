import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import ROLE_ARCHIMAGO, Invite, User
from app.schemas.auth import InviteOut

router = APIRouter(prefix="/invites", tags=["invites"])


def _to_out(inv: Invite) -> InviteOut:
    return InviteOut(
        code=inv.code,
        created_at=inv.created_at,
        used_by=inv.used_by.username if inv.used_by else None,
        used_at=inv.used_at,
    )


@router.get("", response_model=list[InviteOut])
def my_invites(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[InviteOut]:
    invites = db.scalars(
        select(Invite).where(Invite.created_by_id == user.id).order_by(Invite.created_at.desc())
    ).all()
    return [_to_out(i) for i in invites]


@router.post("", response_model=InviteOut, status_code=status.HTTP_201_CREATED)
def create_invite(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> InviteOut:
    if user.role != ROLE_ARCHIMAGO:
        if not user.is_moderator:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Los aprendices no reparten invitaciones")
        if user.invites_left <= 0:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No te quedan invitaciones")
        user.invites_left -= 1
    invite = Invite(code=secrets.token_urlsafe(9), created_by_id=user.id)
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return _to_out(invite)
