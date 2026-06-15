from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "from_attributes": True,
    }


class UserRegister(CamelModel):
    username: str = Field(min_length=3, max_length=40, pattern=r"^[a-zA-Z0-9_\-]+$")
    email: EmailStr
    password: str = Field(min_length=8)
    invite_code: str


class UserLogin(CamelModel):
    username: str  # admite username o email
    password: str


class UserOut(CamelModel):
    id: int
    username: str
    email: str
    role: str
    glyph: str
    invites_left: int
    created_at: datetime


class TokenResponse(CamelModel):
    access_token: str
    user: UserOut


class InviteOut(CamelModel):
    code: str
    created_at: datetime
    used_by: str | None = None
    used_at: datetime | None = None


class ArcaneStats(CamelModel):
    resonancia: float  # 0-100
    estudio: float     # 0-100
    estirpe: float     # 0-100


class UserProfileOut(CamelModel):
    username: str
    role: str
    glyph: str
    created_at: datetime
    artifact_count: int
    adept_count: int
    artifacts: list
    arcane_stats: ArcaneStats
    arcane_title: str | None = None
