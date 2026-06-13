from datetime import datetime

from pydantic import Field

from app.schemas.auth import CamelModel


class ArtifactOut(CamelModel):
    id: str
    title: str
    type: str
    school: str
    era: int
    glyph: str
    media: str
    runes: list[str]
    sealed_by: str
    origin: str
    desc: str
    links: list[str]
    variant_of: str | None = None
    media_url: str | None = None
    source_url: str | None = None
    status: str
    created_at: datetime | None = None


class ArtifactCreate(CamelModel):
    title: str = Field(min_length=1, max_length=160)
    type: str = Field(pattern=r"^(pergamino|reliquia|hechizo|visión)$")
    school: str
    era: int = Field(ge=1970, le=2100)
    glyph: str = Field(default="✦", max_length=8)
    media: str = Field(default="image", pattern=r"^(text|image|audio|video)$")
    runes: list[str] = []
    origin: str = ""
    desc: str = Field(min_length=1)
    links: list[str] = []
    variant_of: str | None = None
    source_url: str | None = None


class ArtifactUpdate(CamelModel):
    title: str | None = None
    type: str | None = None
    school: str | None = None
    era: int | None = None
    glyph: str | None = None
    media: str | None = None
    runes: list[str] | None = None
    origin: str | None = None
    desc: str | None = None
    links: list[str] | None = None
    variant_of: str | None = None
    source_url: str | None = None


class StatusUpdate(CamelModel):
    status: str = Field(pattern=r"^(sellado|rechazado)$")


class SchoolOut(CamelModel):
    id: str
    name: str
    glyph: str
    hue: str
    desc: str
    count: int = 0


class SchoolDetail(CamelModel):
    school: SchoolOut
    artifacts: list[ArtifactOut]


class SpellOut(CamelModel):
    id: str
    name: str
    glyph: str
    hue: str
    desc: str
    tracks: list[str]


class SpellDetail(CamelModel):
    spell: SpellOut
    tracks: list[ArtifactOut]


class NoteOut(CamelModel):
    id: int
    who: str
    glyph: str
    when: datetime
    text: str


class NoteCreate(CamelModel):
    text: str = Field(min_length=1, max_length=2000)


class StatsOut(CamelModel):
    artifacts: int
    connections: int
    schools: int
    since: int
