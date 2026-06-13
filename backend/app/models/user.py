from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Roles: archimago (admin) · mago (sella directo, modera) · aprendiz (propone)
ROLE_ARCHIMAGO = "archimago"
ROLE_MAGO = "mago"
ROLE_APRENDIZ = "aprendiz"
MODERATOR_ROLES = (ROLE_ARCHIMAGO, ROLE_MAGO)

ROLE_GLYPHS = {ROLE_ARCHIMAGO: "⚷", ROLE_MAGO: "⁂", ROLE_APRENDIZ: "✦"}


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default=ROLE_APRENDIZ)
    invites_left: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    invited_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    invited_by: Mapped["User | None"] = relationship(remote_side=[id])

    @property
    def glyph(self) -> str:
        return ROLE_GLYPHS.get(self.role, "✦")

    @property
    def is_moderator(self) -> bool:
        return self.role in MODERATOR_ROLES


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    used_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[User] = relationship(foreign_keys=[created_by_id])
    used_by: Mapped[User | None] = relationship(foreign_keys=[used_by_id])
