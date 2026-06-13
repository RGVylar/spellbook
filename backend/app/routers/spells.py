import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_archimago_user, get_moderator_user, get_optional_user
from app.models.artifact import STATUS_SELLADO, Artifact, Spell
from app.models.user import User
from app.schemas.artifact import ArtifactOut, SpellCreate, SpellDetail, SpellOut, SpellUpdate

router = APIRouter(prefix="/spells", tags=["spells"])


def _slugify_spell(name: str, db: Session) -> str:
    base = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:50] or "hechizo"
    slug, n = base, 2
    while db.get(Spell, slug) is not None:
        slug = f"{base}-{n}"
        n += 1
    return slug


@router.get("", response_model=list[SpellOut])
def list_spells(db: Session = Depends(get_db)) -> list[Spell]:
    return db.scalars(select(Spell)).all()


@router.get("/{spell_id}", response_model=SpellDetail)
def get_spell(spell_id: str, db: Session = Depends(get_db)) -> SpellDetail:
    spell = db.get(Spell, spell_id)
    if spell is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hechizo desconocido")
    tracks = []
    for tid in spell.tracks:
        art = db.get(Artifact, tid)
        if art is not None and art.status == STATUS_SELLADO:
            tracks.append(ArtifactOut.model_validate(art))
    return SpellDetail(spell=SpellOut.model_validate(spell), tracks=tracks)


@router.post("", response_model=SpellOut, status_code=status.HTTP_201_CREATED)
def create_spell(
    payload: SpellCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_moderator_user),
) -> Spell:
    spell = Spell(
        id=_slugify_spell(payload.name, db),
        name=payload.name,
        glyph=payload.glyph,
        hue=payload.hue,
        desc=payload.desc,
        tracks=[],
    )
    db.add(spell)
    db.commit()
    db.refresh(spell)
    return spell


@router.patch("/{spell_id}", response_model=SpellOut)
def update_spell(
    spell_id: str,
    payload: SpellUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_moderator_user),
) -> Spell:
    spell = db.get(Spell, spell_id)
    if spell is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hechizo desconocido")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(spell, key, value)
    db.commit()
    db.refresh(spell)
    return spell


@router.delete("/{spell_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spell(
    spell_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_archimago_user),
) -> None:
    spell = db.get(Spell, spell_id)
    if spell is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hechizo desconocido")
    db.delete(spell)
    db.commit()


@router.post("/{spell_id}/tracks/{artifact_id}", response_model=SpellOut)
def add_track(
    spell_id: str,
    artifact_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_moderator_user),
) -> Spell:
    spell = db.get(Spell, spell_id)
    if spell is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hechizo desconocido")
    art = db.get(Artifact, artifact_id)
    if art is None or art.status != STATUS_SELLADO:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Artefacto no encontrado")
    if art.media not in ("audio", "video"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Solo artefactos de audio o vídeo")
    if artifact_id not in spell.tracks:
        spell.tracks = [*spell.tracks, artifact_id]
        db.commit()
        db.refresh(spell)
    return spell


@router.delete("/{spell_id}/tracks/{artifact_id}", response_model=SpellOut)
def remove_track(
    spell_id: str,
    artifact_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_moderator_user),
) -> Spell:
    spell = db.get(Spell, spell_id)
    if spell is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hechizo desconocido")
    spell.tracks = [t for t in spell.tracks if t != artifact_id]
    db.commit()
    db.refresh(spell)
    return spell
