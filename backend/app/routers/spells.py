from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artifact import STATUS_SELLADO, Artifact, Spell
from app.schemas.artifact import ArtifactOut, SpellDetail, SpellOut

router = APIRouter(prefix="/spells", tags=["spells"])


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
