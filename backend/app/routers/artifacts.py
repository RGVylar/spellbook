import asyncio
import re
import threading
import unicodedata

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_archimago_user, get_current_user, get_moderator_user, get_optional_user
from app.ingest import ingest_url_background, media_path_for, save_upload
from app.models.artifact import (
    STATUS_PENDIENTE,
    STATUS_SELLADO,
    Artifact,
    School,
)
from app.models.user import User
from app.schemas.artifact import ArtifactCreate, ArtifactOut, ArtifactUpdate, StatusUpdate
from app.telegram import send_proposal_alert

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


def _slugify(title: str, db: Session) -> str:
    base = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:50] or "artefacto"
    slug, n = base, 2
    while db.get(Artifact, slug) is not None:
        slug = f"{base}-{n}"
        n += 1
    return slug


@router.get("", response_model=list[ArtifactOut])
def list_artifacts(
    type: str | None = None,
    school: str | None = None,
    rune: str | None = None,
    q: str | None = None,
    variant_of: str | None = Query(None, alias="variantOf"),
    status_: str | None = Query(None, alias="status"),
    mine: bool = False,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
) -> list[Artifact]:
    stmt = select(Artifact).order_by(Artifact.created_at.desc())
    if mine:
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifícate primero")
        stmt = stmt.where(Artifact.created_by_id == user.id)
    elif status_ and status_ != STATUS_SELLADO:
        if user is None or not user.is_moderator:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo los moderadores ven lo no sellado")
        stmt = stmt.where(Artifact.status == status_)
    else:
        stmt = stmt.where(Artifact.status == STATUS_SELLADO)
    if type:
        stmt = stmt.where(Artifact.type == type)
    if school:
        stmt = stmt.where(Artifact.school == school)
    if variant_of:
        stmt = stmt.where(Artifact.variant_of == variant_of)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(func.lower(Artifact.title).like(like), func.lower(Artifact.desc).like(like))
        )
    rows = db.scalars(stmt).all()
    if rune:
        rows = [a for a in rows if rune in (a.runes or [])]
    return rows


@router.get("/pending-count")
def pending_count(
    db: Session = Depends(get_db), user: User = Depends(get_moderator_user)
) -> dict[str, int]:
    n = db.scalar(
        select(func.count()).select_from(Artifact).where(Artifact.status == STATUS_PENDIENTE)
    ) or 0
    return {"count": n}


@router.get("/{artifact_id}", response_model=ArtifactOut)
def get_artifact(
    artifact_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
) -> Artifact:
    art = db.get(Artifact, artifact_id)
    if art is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese artefacto no consta en el grimorio")
    if art.status != STATUS_SELLADO:
        is_owner = user is not None and art.created_by_id == user.id
        if not (is_owner or (user is not None and user.is_moderator)):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese artefacto no consta en el grimorio")
    return art


@router.post("", response_model=ArtifactOut, status_code=status.HTTP_201_CREATED)
def create_artifact(
    payload: ArtifactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Artifact:
    if db.get(School, payload.school) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Escuela desconocida")
    if payload.variant_of is not None and db.get(Artifact, payload.variant_of) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El artefacto madre no existe")
    art = Artifact(
        id=_slugify(payload.title, db),
        title=payload.title,
        type=payload.type,
        school=payload.school,
        era=payload.era,
        glyph=payload.glyph or "✦",
        media=payload.media,
        runes=payload.runes,
        sealed_by=user.username,
        origin=payload.origin,
        desc=payload.desc,
        links=[l for l in payload.links if db.get(Artifact, l) is not None],
        variant_of=payload.variant_of,
        source_url=payload.source_url,
        status=STATUS_SELLADO if user.is_moderator else STATUS_PENDIENTE,
        created_by_id=user.id,
    )
    db.add(art)
    db.commit()
    db.refresh(art)
    if art.status == STATUS_PENDIENTE:
        asyncio.create_task(send_proposal_alert(user.username, art.title, art.id))
    return art


@router.patch("/{artifact_id}", response_model=ArtifactOut)
def update_artifact(
    artifact_id: str,
    payload: ArtifactUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_archimago_user),
) -> Artifact:
    art = db.get(Artifact, artifact_id)
    if art is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese artefacto no consta en el grimorio")
    data = payload.model_dump(exclude_unset=True)
    if "school" in data and db.get(School, data["school"]) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Escuela desconocida")
    if "links" in data:
        data["links"] = [
            l for l in data["links"] if l != art.id and db.get(Artifact, l) is not None
        ]
    if data.get("variant_of") is not None:
        if data["variant_of"] == art.id or db.get(Artifact, data["variant_of"]) is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El artefacto madre no existe")
    for key, value in data.items():
        setattr(art, key, value)
    db.commit()
    db.refresh(art)
    return art


@router.post("/{artifact_id}/media")
async def upload_media(
    artifact_id: str,
    file: UploadFile | None = File(None),
    source_url: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Preserva el archivo de un artefacto: subida directa o ingestión desde URL."""
    art = db.get(Artifact, artifact_id)
    if art is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese artefacto no consta en el grimorio")
    if not user.is_moderator and art.created_by_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo puedes preservar tus propios artefactos")

    if file is not None:
        data = await file.read()
        if len(data) > 200 * 1024 * 1024:  # 200 MB
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "El archivo supera los 200 MB")
        ext, thumb_url = save_upload(data, file.filename or f"media{artifact_id}", artifact_id)
        art.media_url = f"/api/media/{artifact_id}"
        if thumb_url:
            art.thumbnail_url = thumb_url
        db.commit()
        return {"mediaUrl": art.media_url, "thumbnailUrl": art.thumbnail_url, "status": "ready", "ext": ext}

    if source_url:
        # Lanza la descarga en segundo plano para no bloquear la respuesta
        threading.Thread(
            target=ingest_url_background,
            args=(source_url, artifact_id),
            daemon=True,
        ).start()
        return {"mediaUrl": None, "status": "ingesting"}

    raise HTTPException(status.HTTP_400_BAD_REQUEST, "Proporciona file o source_url")


@router.patch("/{artifact_id}/status", response_model=ArtifactOut)
def moderate_artifact(
    artifact_id: str,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_moderator_user),
) -> Artifact:
    art = db.get(Artifact, artifact_id)
    if art is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese artefacto no consta en el grimorio")
    if art.status != STATUS_PENDIENTE:
        raise HTTPException(status.HTTP_409_CONFLICT, "Solo se moderan artefactos pendientes")
    art.status = payload.status
    db.commit()
    db.refresh(art)
    return art
