from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artifact import STATUS_SELLADO, Artifact, School
from app.schemas.artifact import ArtifactOut, SchoolDetail, SchoolOut

router = APIRouter(prefix="/schools", tags=["schools"])


def _counts(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(Artifact.school, func.count())
        .where(Artifact.status == STATUS_SELLADO)
        .group_by(Artifact.school)
    ).all()
    return dict(rows)


@router.get("", response_model=list[SchoolOut])
def list_schools(db: Session = Depends(get_db)) -> list[SchoolOut]:
    counts = _counts(db)
    schools = db.scalars(select(School)).all()
    return [
        SchoolOut(
            id=s.id, name=s.name, glyph=s.glyph, hue=s.hue, desc=s.desc,
            count=counts.get(s.id, 0),
        )
        for s in schools
    ]


@router.get("/{school_id}", response_model=SchoolDetail)
def get_school(school_id: str, db: Session = Depends(get_db)) -> SchoolDetail:
    school = db.get(School, school_id)
    if school is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Escuela desconocida")
    artifacts = db.scalars(
        select(Artifact)
        .where(Artifact.school == school_id, Artifact.status == STATUS_SELLADO)
        .order_by(Artifact.era)
    ).all()
    return SchoolDetail(
        school=SchoolOut(
            id=school.id, name=school.name, glyph=school.glyph, hue=school.hue,
            desc=school.desc, count=len(artifacts),
        ),
        artifacts=[ArtifactOut.model_validate(a) for a in artifacts],
    )
