from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./spellbook.db"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    # Archivos preservados (yt-dlp) — {artifact_id}.{ext}
    media_dir: str = str(Path(__file__).resolve().parents[2] / "media")
    # Cookies de YouTube para vídeos con restricción de edad (formato Netscape/cookies.txt)
    youtube_cookies: str | None = None
    # Ascenso aprendiz → mago
    mago_days: int = 14
    mago_min_approved: int = 1
    mago_invites: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
