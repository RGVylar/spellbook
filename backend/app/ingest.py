"""Ingestión de URLs con yt-dlp — TODO (estructura preparada).

Flujo previsto cuando se implemente:
  1. extract_metadata(url) llama a yt-dlp (-J) para obtener título, canal,
     duración, año y thumbnail sin descargar nada.
  2. El formulario de Invocar/Proponer se autorrellena con esos metadatos.
  3. download(url, artifact_id) descarga el archivo a
     settings.media_dir / f"{artifact_id}.{ext}" y devuelve la ruta.
  4. El artefacto guarda source_url (origen) y media_url (/api/media/{id}),
     quedando preservado localmente aunque el original desaparezca.
"""

from pathlib import Path

from app.config import settings

MEDIA_DIR = Path(settings.media_dir)


def media_path_for(artifact_id: str) -> Path | None:
    """Devuelve el archivo preservado de un artefacto, si existe."""
    if not MEDIA_DIR.is_dir():
        return None
    for f in MEDIA_DIR.iterdir():
        if f.is_file() and f.stem == artifact_id:
            return f
    return None


async def extract_metadata(url: str) -> dict:
    """TODO: yt-dlp -J {url} → {title, channel, duration, year, thumbnail}."""
    raise NotImplementedError("La ingestión con yt-dlp aún no está implementada")


async def download(url: str, artifact_id: str) -> Path:
    """TODO: yt-dlp -o MEDIA_DIR/{artifact_id}.%(ext)s {url}."""
    raise NotImplementedError("La ingestión con yt-dlp aún no está implementada")
