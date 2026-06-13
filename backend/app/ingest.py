"""Preservación de medios: subida directa y descarga desde URL (yt-dlp + httpx)."""
from __future__ import annotations

import re
import threading
from pathlib import Path

import httpx

from app.config import settings

MEDIA_DIR = Path(settings.media_dir)

_IMAGE_EXT_RE = re.compile(r'\.(jpe?g|png|gif|webp|avif|bmp)(\?.*)?$', re.IGNORECASE)
_CT_TO_EXT = {
    'image/jpeg': '.jpg', 'image/jpg': '.jpg',
    'image/png': '.png', 'image/gif': '.gif',
    'image/webp': '.webp', 'image/avif': '.avif',
    'video/mp4': '.mp4', 'video/webm': '.webm',
    'audio/mpeg': '.mp3', 'audio/mp3': '.mp3',
    'audio/ogg': '.ogg', 'audio/wav': '.wav',
}

# Un semáforo para no saturar el servidor con descargas paralelas
_DL_SEMAPHORE = threading.Semaphore(3)


def media_path_for(artifact_id: str) -> Path | None:
    """Devuelve el archivo preservado de un artefacto, si existe."""
    if not MEDIA_DIR.is_dir():
        return None
    for f in MEDIA_DIR.iterdir():
        if f.is_file() and f.stem == artifact_id:
            return f
    return None


def save_upload(data: bytes, original_filename: str, artifact_id: str) -> str:
    """Guarda bytes subidos directamente. Devuelve la extensión (.jpg, .mp4…)."""
    ext = Path(original_filename).suffix.lower() or '.bin'
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    dest = MEDIA_DIR / f"{artifact_id}{ext}"
    dest.write_bytes(data)
    return ext


def _is_direct_image(url: str) -> bool:
    return bool(_IMAGE_EXT_RE.search(url.split('?')[0]))


def _download_image(url: str, artifact_id: str) -> str:
    """Descarga imagen directa vía httpx. Devuelve extensión."""
    with httpx.Client(follow_redirects=True, timeout=30) as client:
        r = client.get(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; Spellbook/1.0)'})
        r.raise_for_status()
        ct = r.headers.get('content-type', '').split(';')[0].strip()
        ext = _CT_TO_EXT.get(ct) or Path(url.split('?')[0]).suffix.lower() or '.jpg'
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        (MEDIA_DIR / f"{artifact_id}{ext}").write_bytes(r.content)
        return ext


def _run_ytdlp(url: str, artifact_id: str) -> str:
    """Descarga con yt-dlp (vídeo/audio). Devuelve extensión."""
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError("yt-dlp no está instalado en este entorno")

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    outtmpl = str(MEDIA_DIR / f"{artifact_id}.%(ext)s")
    ydl_opts = {
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'format': (
            'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]'
            '/best[height<=720][ext=mp4]/best[ext=mp4]/best'
        ),
        'merge_output_format': 'mp4',
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
    }
    with _DL_SEMAPHORE:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    path = media_path_for(artifact_id)
    if path is None:
        raise RuntimeError("yt-dlp no produjo ningún archivo de salida")
    return path.suffix


def ingest_url_background(url: str, artifact_id: str) -> None:
    """Descarga url y actualiza media_url en el artefacto. Diseñado para correr en hilo."""
    from app.database import SessionLocal
    from app.models.artifact import Artifact

    print(f"[INGEST] Iniciando preservación de {artifact_id} desde {url}")
    try:
        if _is_direct_image(url):
            ext = _download_image(url, artifact_id)
        else:
            ext = _run_ytdlp(url, artifact_id)

        db = SessionLocal()
        try:
            art = db.get(Artifact, artifact_id)
            if art:
                art.media_url = f"/api/media/{artifact_id}"
                db.commit()
            print(f"[INGEST] Preservado {artifact_id}{ext} ✓")
        finally:
            db.close()
    except Exception as exc:
        print(f"[INGEST] Error preservando {artifact_id}: {exc}")
