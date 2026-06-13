from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artifact import STATUS_SELLADO, Artifact
from app.models.user import User
from app.schemas.artifact import ArtifactOut
from app.schemas.auth import UserProfileOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{username}", response_model=UserProfileOut)
def get_profile(username: str, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese mago no figura en el grimorio")
    artifacts = db.scalars(
        select(Artifact)
        .where(Artifact.created_by_id == user.id, Artifact.status == STATUS_SELLADO)
        .order_by(Artifact.created_at.desc())
    ).all()
    return {
        "username": user.username,
        "role": user.role,
        "glyph": user.glyph,
        "created_at": user.created_at,
        "artifact_count": len(artifacts),
        "artifacts": [
            ArtifactOut.model_validate({**a.__dict__, "user_reaction": None, "note_count": 0})
            for a in artifacts
        ],
    }
