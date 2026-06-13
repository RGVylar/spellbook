"""Stats, runas y media preservada."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.ingest import media_path_for
from app.models.artifact import STATUS_SELLADO, Artifact, School
from app.schemas.artifact import StatsOut

router = APIRouter(tags=["misc"])

# Runas canónicas del grimorio; se amplían con las que traigan los artefactos
BASE_RUNES = [
    "viral", "banger", "og", "clásico", "copypasta", "maldito", "irónico", "wholesome",
    "bait", "loop", "plantilla", "brainrot", "reacción", "danza", "webcam", "stock",
    "2007", "profundo",
]


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)) -> StatsOut:
    arts = db.scalars(select(Artifact).where(Artifact.status == STATUS_SELLADO)).all()
    schools = db.scalar(select(func.count()).select_from(School)) or 0
    since = min((a.era for a in arts), default=2020)
    return StatsOut(
        artifacts=len(arts),
        connections=sum(len(a.links or []) for a in arts),
        schools=schools,
        since=since,
    )


@router.get("/runes")
def runes(db: Session = Depends(get_db)) -> list[str]:
    seen = list(BASE_RUNES)
    arts = db.scalars(select(Artifact).where(Artifact.status == STATUS_SELLADO)).all()
    for a in arts:
        for r in a.runes or []:
            if r not in seen:
                seen.append(r)
    return seen


_MIME = {
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
    '.gif': 'image/gif', '.webp': 'image/webp', '.avif': 'image/avif',
    '.mp4': 'video/mp4', '.webm': 'video/webm',
    '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.wav': 'audio/wav',
}


@router.get("/media/{artifact_id}/thumb")
def media_thumb(artifact_id: str) -> FileResponse:
    from pathlib import Path
    from app.config import settings
    thumb = Path(settings.media_dir) / f"{artifact_id}_thumb.jpg"
    if not thumb.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thumbnail no disponible")
    return FileResponse(thumb, media_type="image/jpeg")


@router.get("/media/{artifact_id}")
def media(artifact_id: str) -> FileResponse:
    path = media_path_for(artifact_id)
    if path is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Este artefacto aún no fue preservado")
    mime = _MIME.get(path.suffix.lower(), 'application/octet-stream')
    return FileResponse(path, media_type=mime)
