import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import artifacts, auth, invites, misc, notes, schools, spells
from app.telegram import send_error_alert

# Transient network errors — log but don't spam Telegram
_SILENT_EXCEPTIONS = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
)

app = FastAPI(title="Spellbook", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, _SILENT_EXCEPTIONS):
        return JSONResponse(status_code=503, content={"detail": "Servicio externo no disponible, inténtalo de nuevo"})
    await send_error_alert(request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "El grimorio ha sufrido una perturbación"})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


api_prefix = "/api"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(invites.router, prefix=api_prefix)
app.include_router(artifacts.router, prefix=api_prefix)
app.include_router(schools.router, prefix=api_prefix)
app.include_router(spells.router, prefix=api_prefix)
app.include_router(notes.router, prefix=api_prefix)
app.include_router(misc.router, prefix=api_prefix)
