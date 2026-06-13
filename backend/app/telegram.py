"""Telegram alerts for Spellbook — errores y eventos clave para el Archimago."""

import traceback
from datetime import datetime, timezone

import httpx

from app.config import settings

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"

_PAYLOAD_BASE = {"parse_mode": "Markdown"}


def _payload(text: str) -> dict:
    return {**_PAYLOAD_BASE, "chat_id": settings.telegram_chat_id, "text": text}


async def _send(text: str) -> None:
    """Fire-and-forget async. Silently ignores send failures."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(
                TELEGRAM_API.format(token=settings.telegram_bot_token),
                json=_payload(text),
            )
    except Exception:
        pass


def _send_sync(text: str) -> None:
    """Fire-and-forget sync (para hilos de background). Silently ignores failures."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
    try:
        with httpx.Client(timeout=5) as client:
            client.post(
                TELEGRAM_API.format(token=settings.telegram_bot_token),
                json=_payload(text),
            )
    except Exception:
        pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


async def send_error_alert(method: str, path: str, exc: Exception) -> None:
    """500 — unhandled server exception."""
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_short = "".join(tb_lines[-8:]).strip()
    text = (
        f"🔴 *[spellbook]* Error 500 — `{method} {path}`\n\n"
        f"`{type(exc).__name__}: {exc}`\n\n"
        f"```\n{tb_short}\n```\n\n"
        f"🕐 {_now()}"
    )
    await _send(text)


async def send_new_user_alert(username: str, invited_by: str | None, user_count: int) -> None:
    """Nuevo aprendiz registrado."""
    text = (
        f"👤 *[spellbook]* Nuevo aprendiz\n\n"
        f"*Usuario:* {username}\n"
        f"*Invitado por:* {invited_by or '—'}\n"
        f"*Total usuarios:* {user_count}\n\n"
        f"🕐 {_now()}"
    )
    await _send(text)


async def send_proposal_alert(username: str, title: str, artifact_id: str) -> None:
    """Un aprendiz propone un artefacto — pendiente de moderación."""
    text = (
        f"📜 *[spellbook]* Propuesta pendiente\n\n"
        f"*Artefacto:* {title}\n"
        f"*Aprendiz:* {username}\n"
        f"*Id:* `{artifact_id}`\n\n"
        f"🕐 {_now()}"
    )
    await _send(text)


def send_new_user_alert_sync(username: str, invited_by: str | None, user_count: int) -> None:
    text = (
        f"👤 *[spellbook]* Nuevo aprendiz\n\n"
        f"*Usuario:* {username}\n"
        f"*Invitado por:* {invited_by or '—'}\n"
        f"*Total usuarios:* {user_count}\n\n"
        f"🕐 {_now()}"
    )
    _send_sync(text)


def send_proposal_alert_sync(username: str, title: str, artifact_id: str) -> None:
    text = (
        f"📜 *[spellbook]* Propuesta pendiente\n\n"
        f"*Artefacto:* {title}\n"
        f"*Aprendiz:* {username}\n"
        f"*Id:* `{artifact_id}`\n\n"
        f"🕐 {_now()}"
    )
    _send_sync(text)


def send_ingest_success_sync(artifact_id: str, url: str, ext: str, size_mb: float) -> None:
    """Preservación completada con éxito (sync, para hilos)."""
    text = (
        f"✅ *[spellbook]* Preservado\n\n"
        f"*Artefacto:* `{artifact_id}`\n"
        f"*Formato:* `{ext}` · *Peso:* {size_mb:.1f} MB\n"
        f"*Fuente:* `{url[:80]}`\n\n"
        f"🕐 {_now()}"
    )
    _send_sync(text)


def send_ingest_error_sync(artifact_id: str, url: str, exc: Exception) -> None:
    """Preservación fallida (sync, para hilos)."""
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_short = "".join(tb_lines[-6:]).strip()
    text = (
        f"⚠️ *[spellbook]* Ingest fallido\n\n"
        f"*Artefacto:* `{artifact_id}`\n"
        f"*Fuente:* `{url[:80]}`\n"
        f"`{type(exc).__name__}: {exc}`\n\n"
        f"```\n{tb_short}\n```\n\n"
        f"🕐 {_now()}"
    )
    _send_sync(text)
