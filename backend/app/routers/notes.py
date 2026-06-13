from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user
from app.models.artifact import Artifact, Note
from app.models.user import User
from app.schemas.artifact import NoteCreate, NoteOut

router = APIRouter(prefix="/artifacts", tags=["notes"])


def _to_out(note: Note) -> NoteOut:
    return NoteOut(
        id=note.id,
        who=note.user.username,
        glyph=note.user.glyph,
        when=note.created_at,
        text=note.text,
    )


@router.get("/{artifact_id}/notes", response_model=list[NoteOut])
def list_notes(artifact_id: str, db: Session = Depends(get_db)) -> list[NoteOut]:
    if db.get(Artifact, artifact_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese artefacto no consta en el grimorio")
    notes = db.scalars(
        select(Note)
        .where(Note.artifact_id == artifact_id)
        .order_by(Note.created_at.desc())
        .options(joinedload(Note.user))
    ).all()
    return [_to_out(n) for n in notes]


@router.post(
    "/{artifact_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED
)
def create_note(
    artifact_id: str,
    payload: NoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> NoteOut:
    if db.get(Artifact, artifact_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese artefacto no consta en el grimorio")
    note = Note(artifact_id=artifact_id, user_id=user.id, text=payload.text.strip())
    db.add(note)
    db.commit()
    db.refresh(note)
    return _to_out(note)
