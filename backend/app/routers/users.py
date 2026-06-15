import math

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artifact import STATUS_SELLADO, Artifact, ArtifactStudied
from app.models.user import User
from app.schemas.artifact import ArtifactOut
from app.schemas.auth import ArcaneStats, UserProfileOut

router = APIRouter(prefix="/users", tags=["users"])

SCHOOL_TITLES: dict[str, str] = {
    "caos":          "Heraldo del Caos",
    "nigromancia":   "Señor de los Muertos",
    "ilusionismo":   "Arquitecto de Espejismos",
    "invocacion":    "Gran Invocador",
    "cacofonia":     "Señor del Estruendo",
    "adivinacion":   "Vidente Eterno",
    "transmutacion": "Gran Transmutor",
    "cronomancia":   "Señor del Tiempo",
}


def _compute_arcane_title(user: User, db: Session) -> str | None:
    """Devuelve el título arcano basado en la escuela dominante del usuario."""
    row = db.execute(
        select(Artifact.school, func.count(Artifact.id).label("n"))
        .where(Artifact.created_by_id == user.id, Artifact.status == STATUS_SELLADO)
        .group_by(Artifact.school)
        .order_by(func.count(Artifact.id).desc())
        .limit(1)
    ).first()
    if row is None:
        return None
    return SCHOOL_TITLES.get(row.school)


def _compute_arcane_stats(user: User, db: Session) -> ArcaneStats:
    # Resonancia: suma de views de todos los artefactos sellados por este usuario.
    # Escala logarítmica: 1000 views ≈ 100 puntos.
    total_views = db.scalar(
        select(func.coalesce(func.sum(Artifact.views), 0)).where(
            Artifact.created_by_id == user.id,
            Artifact.status == STATUS_SELLADO,
        )
    ) or 0
    resonancia = min(math.log10(total_views + 1) / math.log10(1001) * 100, 100.0)

    # Estudio: % de artefactos sellados en el grimorio que ha visto este usuario.
    total_artifacts = db.scalar(
        select(func.count(Artifact.id)).where(Artifact.status == STATUS_SELLADO)
    ) or 0
    studied = db.scalar(
        select(func.count(ArtifactStudied.id)).where(ArtifactStudied.user_id == user.id)
    ) or 0
    estudio = (studied / total_artifacts * 100) if total_artifacts > 0 else 0.0

    # Estirpe: tamaño del árbol de invitados recursivo (CTE).
    # 50 descendientes ≈ 100 puntos (escala logarítmica suave).
    result = db.execute(
        text("""
            WITH RECURSIVE tree(id) AS (
                SELECT id FROM users WHERE invited_by_id = :uid
                UNION ALL
                SELECT u.id FROM users u JOIN tree t ON u.invited_by_id = t.id
            )
            SELECT COUNT(*) FROM tree
        """),
        {"uid": user.id},
    ).scalar()
    lineage_size = result or 0
    estirpe = min(math.log10(lineage_size + 1) / math.log10(51) * 100, 100.0)

    return ArcaneStats(resonancia=resonancia, estudio=estudio, estirpe=estirpe)


def _build_lineage_node(user: User, all_users: list[User]) -> dict:
    children = [u for u in all_users if u.invited_by_id == user.id]
    return {
        "username": user.username,
        "role": user.role,
        "glyph": user.glyph,
        "children": [_build_lineage_node(c, all_users) for c in children],
    }


@router.get("/{username}/lineage")
def get_lineage(username: str, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese mago no figura en el grimorio")
    # Obtener todo el árbol de descendientes via CTE, luego construir en Python
    descendant_ids_result = db.execute(
        text("""
            WITH RECURSIVE tree(id) AS (
                SELECT id FROM users WHERE invited_by_id = :uid
                UNION ALL
                SELECT u.id FROM users u JOIN tree t ON u.invited_by_id = t.id
            )
            SELECT id FROM tree
        """),
        {"uid": user.id},
    ).scalars().all()
    descendant_ids = list(descendant_ids_result)
    descendants = (
        db.scalars(select(User).where(User.id.in_(descendant_ids))).all()
        if descendant_ids
        else []
    )
    all_users = [user, *descendants]
    return _build_lineage_node(user, all_users)


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
    adept_count = db.scalar(
        select(func.count(User.id)).where(User.invited_by_id == user.id)
    ) or 0
    arcane_stats = _compute_arcane_stats(user, db)
    arcane_title = _compute_arcane_title(user, db)
    return {
        "username": user.username,
        "role": user.role,
        "glyph": user.glyph,
        "created_at": user.created_at,
        "artifact_count": len(artifacts),
        "adept_count": adept_count,
        "artifacts": [
            ArtifactOut.model_validate({**a.__dict__, "user_reaction": None, "note_count": 0})
            for a in artifacts
        ],
        "arcane_stats": arcane_stats,
        "arcane_title": arcane_title,
    }
