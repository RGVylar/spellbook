"""Stats, runas y media preservada."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_archimago_user
from app.ingest import media_path_for
from app.models.artifact import STATUS_PENDIENTE, STATUS_RECHAZADO, STATUS_SELLADO, Artifact, Note, ArtifactReaction, School
from app.models.user import User
from app.schemas.artifact import AdminStatsOut, ArtifactMini, SchoolCount, StatsOut

router = APIRouter(tags=["misc"])

# Runas canónicas del grimorio; se amplían con las que traigan los artefactos
BASE_RUNES = [
    "viral", "banger", "og", "clásico", "copypasta", "maldito", "irónico", "wholesome",
    "bait", "loop", "plantilla", "brainrot", "reacción", "danza", "webcam", "stock",
    "2007", "profundo",
]


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)) -> StatsOut:
    artifact_count = db.scalar(
        select(func.count()).select_from(Artifact).where(Artifact.status == STATUS_SELLADO)
    ) or 0
    since = db.scalar(
        select(func.min(Artifact.era)).where(Artifact.status == STATUS_SELLADO)
    ) or 2020
    all_links = db.scalars(
        select(Artifact.links).where(Artifact.status == STATUS_SELLADO)
    ).all()
    connections = sum(len(links or []) for links in all_links)
    schools = db.scalar(select(func.count()).select_from(School)) or 0
    mages = db.scalar(select(func.count()).select_from(User)) or 0
    return StatsOut(
        artifacts=artifact_count,
        connections=connections,
        schools=schools,
        since=since,
        mages=mages,
    )


@router.get("/admin/stats", response_model=AdminStatsOut)
def admin_stats(db: Session = Depends(get_db), _: User = Depends(get_archimago_user)) -> AdminStatsOut:
    def count_where(**kwargs):
        stmt = select(func.count()).select_from(Artifact)
        for col, val in kwargs.items():
            stmt = stmt.where(getattr(Artifact, col) == val)
        return db.scalar(stmt) or 0

    total = count_where()
    sellado = count_where(status=STATUS_SELLADO)
    pendiente = count_where(status=STATUS_PENDIENTE)
    rechazado = count_where(status=STATUS_RECHAZADO)

    # Por tipo y media (sobre todos los artefactos)
    rows_type = db.execute(
        select(Artifact.type, func.count()).group_by(Artifact.type)
    ).all()
    by_type = {r[0]: r[1] for r in rows_type}

    rows_media = db.execute(
        select(Artifact.media, func.count()).group_by(Artifact.media)
    ).all()
    by_media = {r[0]: r[1] for r in rows_media}

    # Por escuela (sellados)
    schools = db.scalars(select(School)).all()
    rows_school = db.execute(
        select(Artifact.school, func.count())
        .where(Artifact.status == STATUS_SELLADO)
        .group_by(Artifact.school)
    ).all()
    school_counts = {r[0]: r[1] for r in rows_school}
    by_school = [
        SchoolCount(id=s.id, name=s.name, glyph=s.glyph, hue=s.hue, count=school_counts.get(s.id, 0))
        for s in schools
    ]
    by_school.sort(key=lambda x: x.count, reverse=True)

    # Usuarios por rol
    rows_role = db.execute(
        select(User.role, func.count()).group_by(User.role)
    ).all()
    by_role = {r[0]: r[1] for r in rows_role}
    total_users = sum(by_role.values())

    # Top 5 por vistas y likes (sellados)
    top_views_rows = db.scalars(
        select(Artifact)
        .where(Artifact.status == STATUS_SELLADO)
        .order_by(Artifact.views.desc())
        .limit(5)
    ).all()
    top_likes_rows = db.scalars(
        select(Artifact)
        .where(Artifact.status == STATUS_SELLADO)
        .order_by(Artifact.likes.desc())
        .limit(5)
    ).all()

    def to_mini(a: Artifact) -> ArtifactMini:
        return ArtifactMini(id=a.id, title=a.title, school=a.school, views=a.views, likes=a.likes)

    # Anotaciones y reacciones totales
    total_notes = db.scalar(select(func.count()).select_from(Note)) or 0
    total_reactions = db.scalar(select(func.count()).select_from(ArtifactReaction)) or 0

    # Conexiones (enlaces entre sellados)
    all_links = db.scalars(select(Artifact.links).where(Artifact.status == STATUS_SELLADO)).all()
    total_connections = sum(len(lnk or []) for lnk in all_links)

    return AdminStatsOut(
        total=total,
        sellado=sellado,
        pendiente=pendiente,
        rechazado=rechazado,
        by_type=by_type,
        by_media=by_media,
        by_school=by_school,
        total_users=total_users,
        by_role=by_role,
        top_views=[to_mini(a) for a in top_views_rows],
        top_likes=[to_mini(a) for a in top_likes_rows],
        total_notes=total_notes,
        total_reactions=total_reactions,
        total_connections=total_connections,
    )


@router.get("/runes")
def runes(db: Session = Depends(get_db)) -> list[str]:
    seen = list(BASE_RUNES)
    seen_set = set(BASE_RUNES)
    all_runes = db.scalars(
        select(Artifact.runes).where(Artifact.status == STATUS_SELLADO)
    ).all()
    for rune_list in all_runes:
        for r in rune_list or []:
            if r not in seen_set:
                seen.append(r)
                seen_set.add(r)
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
