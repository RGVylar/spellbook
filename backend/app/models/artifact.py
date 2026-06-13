from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Estados de moderación: las propuestas de aprendices nacen 'pendiente'
STATUS_SELLADO = "sellado"
STATUS_PENDIENTE = "pendiente"
STATUS_RECHAZADO = "rechazado"


class School(Base):
    __tablename__ = "schools"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    glyph: Mapped[str] = mapped_column(String(8), nullable=False)
    hue: Mapped[str] = mapped_column(String(16), nullable=False)
    desc: Mapped[str] = mapped_column("description", Text, nullable=False)


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # pergamino|reliquia|hechizo|visión
    school: Mapped[str] = mapped_column(ForeignKey("schools.id"), nullable=False)
    era: Mapped[int] = mapped_column(Integer, nullable=False)
    glyph: Mapped[str] = mapped_column(String(8), nullable=False, default="✦")
    media: Mapped[str] = mapped_column(String(8), nullable=False, default="image")  # text|image|audio|video
    runes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    sealed_by: Mapped[str] = mapped_column(String(80), nullable=False)
    origin: Mapped[str] = mapped_column(Text, nullable=False, default="")
    desc: Mapped[str] = mapped_column("description", Text, nullable=False, default="")
    links: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # Linaje: este artefacto es una variante/derivado de otro (plantilla madre)
    variant_of: Mapped[str | None] = mapped_column(ForeignKey("artifacts.id"), nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)  # origen yt-dlp
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=STATUS_SELLADO)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    notes: Mapped[list["Note"]] = relationship(
        back_populates="artifact", cascade="all, delete-orphan"
    )


class Spell(Base):
    __tablename__ = "spells"

    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    glyph: Mapped[str] = mapped_column(String(8), nullable=False)
    hue: Mapped[str] = mapped_column(String(16), nullable=False)
    desc: Mapped[str] = mapped_column("description", Text, nullable=False)
    tracks: Mapped[list] = mapped_column(JSON, nullable=False, default=list)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    artifact: Mapped[Artifact] = relationship(back_populates="notes")
    user: Mapped["User"] = relationship()  # noqa: F821
