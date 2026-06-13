#!/usr/bin/env bash
# Spellbook LXC installer (Debian 12) — mismo patrón que deus-vault
# Usage (inside the LXC, as root):
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/RGVylar/spellbook/main/deploy/install.sh)"
#
# Idempotent-ish: re-running will update code and restart services.

set -euo pipefail

# ---------- pretty output ----------
RED=$'\033[0;31m'; GRN=$'\033[0;32m'; YLW=$'\033[1;33m'; BLU=$'\033[0;34m'; NC=$'\033[0m'
msg()  { echo -e "${BLU}[*]${NC} $*"; }
ok()   { echo -e "${GRN}[+]${NC} $*"; }
warn() { echo -e "${YLW}[!]${NC} $*"; }
die()  { echo -e "${RED}[x]${NC} $*" >&2; exit 1; }

[[ $EUID -eq 0 ]] || die "Run as root inside the LXC."

# ---------- config ----------
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
if [[ -n "$GITHUB_TOKEN" ]]; then
    REPO_URL="${REPO_URL:-https://${GITHUB_TOKEN}@github.com/RGVylar/spellbook.git}"
else
    REPO_URL="${REPO_URL:-https://github.com/RGVylar/spellbook.git}"
fi
REPO_BRANCH="${REPO_BRANCH:-main}"
APP_DIR="${APP_DIR:-/opt/spellbook}"
APP_USER="${APP_USER:-spellbook}"

DB_NAME="${DB_NAME:-spellbook}"
DB_USER="${DB_USER:-spellbook}"
DB_PASS="${DB_PASS:-$(openssl rand -hex 16)}"

DOMAIN="${DOMAIN:-spellbook.mugrelore.com}"
BACKEND_PORT="${BACKEND_PORT:-8001}"
JWT_SECRET="${JWT_SECRET:-$(openssl rand -hex 32)}"

# Telegram (opcional) — conserva valores previos si existen
EXISTING_TG_TOKEN=""
EXISTING_TG_CHAT=""
if [[ -f "$APP_DIR/backend/.env" ]]; then
    EXISTING_TG_TOKEN="$(grep '^TELEGRAM_BOT_TOKEN=' "$APP_DIR/backend/.env" | cut -d '=' -f2- || true)"
    EXISTING_TG_CHAT="$(grep '^TELEGRAM_CHAT_ID=' "$APP_DIR/backend/.env" | cut -d '=' -f2- || true)"
fi
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-$EXISTING_TG_TOKEN}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-$EXISTING_TG_CHAT}"

export DEBIAN_FRONTEND=noninteractive

# ---------- packages ----------
msg "Installing system packages…"
apt-get update -qq
apt-get install -y -qq \
    curl ca-certificates gnupg lsb-release git \
    python3 python3-venv python3-pip \
    postgresql postgresql-contrib \
    build-essential libpq-dev \
    debian-keyring debian-archive-keyring apt-transport-https \
    ffmpeg \
    sudo
ok "Base packages installed"

# Fix locale warnings
if ! locale -a 2>/dev/null | grep -q "en_US.utf8"; then
    msg "Generating locale en_US.UTF-8…"
    sed -i 's/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen 2>/dev/null || true
    locale-gen en_US.UTF-8 >/dev/null 2>&1 || true
fi
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Caddy
if ! command -v caddy >/dev/null 2>&1; then
    msg "Installing Caddy…"
    curl -fsSL https://dl.cloudsmith.io/public/caddy/stable/gpg.key \
        | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -fsSL https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt \
        > /etc/apt/sources.list.d/caddy-stable.list
    apt-get update -qq
    apt-get install -y -qq caddy
    ok "Caddy installed"
fi

# Node.js (for SvelteKit build) — LTS via nodesource
if ! command -v node >/dev/null 2>&1; then
    msg "Installing Node.js LTS…"
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - || die "Failed to add NodeSource repo"
    apt-get install -y -qq nodejs || die "Failed to install Node.js"
    ok "Node $(node -v) installed"
fi

# ---------- system user ----------
if ! id "$APP_USER" >/dev/null 2>&1; then
    msg "Creating system user $APP_USER…"
    useradd --system --create-home --home-dir "/home/$APP_USER" --shell /usr/sbin/nologin "$APP_USER"
fi

# ---------- code ----------
if [[ -d "$APP_DIR/.git" ]]; then
    msg "Updating existing checkout at $APP_DIR…"
    git -C "$APP_DIR" fetch --quiet origin "$REPO_BRANCH"
    git -C "$APP_DIR" reset --hard "origin/$REPO_BRANCH"
else
    msg "Cloning $REPO_URL → $APP_DIR…"
    DISPLAY_URL="$REPO_URL"
    [[ -n "$GITHUB_TOKEN" ]] && DISPLAY_URL="${DISPLAY_URL//${GITHUB_TOKEN}/@github_token@}"
    msg "  → $DISPLAY_URL"
    git clone --quiet --branch "$REPO_BRANCH" "$REPO_URL" "$APP_DIR" || die "Clone failed (check GITHUB_TOKEN if private repo)"
fi
mkdir -p "$APP_DIR/media"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
ok "Code in place"

# ---------- postgres ----------
msg "Configuring PostgreSQL…"
systemctl enable --now postgresql >/dev/null

DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" || true)
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" || true)

if [[ "$USER_EXISTS" != "1" ]]; then
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" >/dev/null
    ok "Created DB user $DB_USER"
else
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASS';" >/dev/null
    warn "DB user existed; password reset"
fi

if [[ "$DB_EXISTS" != "1" ]]; then
    sudo -u postgres createdb -O "$DB_USER" "$DB_NAME"
    ok "Created database $DB_NAME"
fi

# ---------- backend venv ----------
msg "Setting up backend venv…"
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/backend/.venv"
sudo -u "$APP_USER" "$APP_DIR/backend/.venv/bin/pip" install --quiet --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/backend/.venv/bin/pip" install --quiet -e "$APP_DIR/backend"
ok "Python deps installed"

# ---------- backend .env ----------
msg "Writing backend .env…"
cat > "$APP_DIR/backend/.env" <<EOF
DATABASE_URL=postgresql+psycopg2://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID
MEDIA_DIR=$APP_DIR/media
EOF
chown "$APP_USER:$APP_USER" "$APP_DIR/backend/.env"
chmod 600 "$APP_DIR/backend/.env"

# ---------- migrations + seed ----------
msg "Running Alembic migrations…"
sleep 2
sudo -u "$APP_USER" bash -c "cd $APP_DIR/backend && .venv/bin/alembic upgrade head"
ok "Migrations applied"

msg "Seeding grimorio (idempotente)…"
sudo -u "$APP_USER" bash -c "cd $APP_DIR/backend && set -a && source .env && set +a && \
    ARCHIMAGO_USERNAME='${ARCHIMAGO_USERNAME:-archimago}' \
    ARCHIMAGO_EMAIL='${ARCHIMAGO_EMAIL:-rgvylar@gmail.com}' \
    ARCHIMAGO_PASSWORD='${ARCHIMAGO_PASSWORD:-}' \
    .venv/bin/python -m scripts.seed"
ok "Seed done (guarda la contraseña del Archimago si se generó arriba)"

# ---------- frontend build ----------
if [[ -f "$APP_DIR/frontend/package.json" ]]; then
    msg "Building frontend…"
    sudo -u "$APP_USER" bash -c "cd $APP_DIR/frontend && npm install --silent && npm run build --silent"
    ok "Frontend built"
else
    warn "Frontend not present yet — skipping"
fi

# ---------- systemd: backend ----------
msg "Installing systemd units…"
install -m 644 "$APP_DIR/deploy/spellbook-backend.service" /etc/systemd/system/spellbook-backend.service

# ---------- caddy ----------
msg "Configuring Caddy…"
sed -e "s|__BACKEND_PORT__|$BACKEND_PORT|" -e "s|__APP_DIR__|$APP_DIR|" \
    "$APP_DIR/deploy/Caddyfile" > /etc/caddy/Caddyfile

systemctl daemon-reload
systemctl enable --now spellbook-backend.service >/dev/null
systemctl restart spellbook-backend.service
systemctl reload caddy
ok "Services up"

cat <<EOF

${GRN}✔ Spellbook installed${NC}

  Backend:   http://127.0.0.1:$BACKEND_PORT/health
  Domain:    https://$DOMAIN  (point your Cloudflare Tunnel to 127.0.0.1:80)
  DB:        postgresql://$DB_USER:***@localhost:5432/$DB_NAME
  App dir:   $APP_DIR
  Media:     $APP_DIR/media  (archivos preservados por yt-dlp)
  Logs:      journalctl -u spellbook-backend -f

${YLW}Save this DB password if you didn't set one explicitly:${NC}
  $DB_PASS
EOF
