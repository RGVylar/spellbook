# SPELLBOOK ✦

> _omnia memes in unum_ — el Svalbard Seed Vault de la cultura meme. Un grimorio digital donde cada meme, canción viral y copypasta queda documentado, vinculado y sellado para la posteridad.

## Stack

- **Frontend** — SvelteKit 2 · Svelte 5 (runes) · TypeScript · CSS propio con design tokens (sin librerías de UI) · `adapter-static` (SPA)
- **Backend** — FastAPI · SQLAlchemy 2 + Alembic · Pydantic v2 · JWT (python-jose + bcrypt) · SQLite en dev / PostgreSQL en prod
- **Deploy** — Caddy (reverse proxy) + systemd en un LXC de Proxmox

## Roles

| Rol | Quién | Poderes |
|---|---|---|
| **Archimago** | el dueño del grimorio | todo: sella, edita, modera, invitaciones ilimitadas |
| **Mago** | 14 días + ≥1 propuesta aprobada (ascenso automático) | sella directo, modera propuestas, 10 invitaciones |
| **Aprendiz** | cuenta recién iniciada | propone artefactos (moderados), anota en los márgenes |
| **Profano** | sin cuenta | contempla el grimorio entero, no añade nada |

El registro es **solo por invitación** (estilo Forocoches): cada código es de un solo uso y queda registrado quién invitó a quién. Cuando un aprendiz propone un artefacto, el Archimago recibe aviso por Telegram.

## Desarrollo

```bash
# Backend (puerto 8001)
cd backend
python -m venv .venv && .venv/Scripts/pip install -e .   # Windows
alembic upgrade head
python -m scripts.seed        # crea archimago + primera invitación + 21 artefactos
uvicorn app.main:app --port 8001 --reload

# Frontend (proxy /api → 8001)
cd frontend
npm install
npm run dev
```

## Producción

```bash
# dentro del LXC, como root:
bash -c "$(curl -fsSL https://raw.githubusercontent.com/RGVylar/spellbook/main/deploy/install.sh)"
```

Variables útiles: `DOMAIN`, `ARCHIMAGO_PASSWORD`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

## Estructura

```
spellbook/
├── backend/          # FastAPI: app/{models,routers,schemas}, alembic, scripts/seed.py
├── frontend/         # SvelteKit: lib/{components,stores,styles}, routes
├── media/            # archivos preservados por yt-dlp (futuro ingest.py)
└── deploy/           # Caddyfile, spellbook-backend.service, install.sh
```

_Que perdure mil años._ ✦
