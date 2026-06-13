"""Siembra el grimorio: tablas, escuelas, artefactos, hechizos y el Archimago.

Idempotente: no duplica lo que ya existe. Uso:
    python -m scripts.seed          (desde backend/, con el venv activo)

Variables de entorno opcionales para la cuenta del Archimago:
    ARCHIMAGO_USERNAME (default: archimago)
    ARCHIMAGO_EMAIL    (default: archimago@spellbook.local)
    ARCHIMAGO_PASSWORD (default: generada y mostrada por consola)
"""

import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app import models  # noqa: F401, E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.artifact import STATUS_SELLADO, Artifact, School, Spell  # noqa: E402
from app.models.user import ROLE_ARCHIMAGO, Invite, User  # noqa: E402
from app.security import hash_password  # noqa: E402
from app.seed_data import ARTIFACTS, SCHOOLS, SPELLS  # noqa: E402


def main() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        for s in SCHOOLS:
            if db.get(School, s["id"]) is None:
                db.add(School(**s))
        db.flush()

        for a in ARTIFACTS:
            if db.get(Artifact, a["id"]) is None:
                db.add(Artifact(**a, status=STATUS_SELLADO))
        db.flush()

        for sp in SPELLS:
            if db.get(Spell, sp["id"]) is None:
                db.add(Spell(**sp))

        username = os.environ.get("ARCHIMAGO_USERNAME", "archimago")
        archimago = db.scalar(select(User).where(User.username == username))
        if archimago is None:
            password = os.environ.get("ARCHIMAGO_PASSWORD") or secrets.token_urlsafe(12)
            archimago = User(
                username=username,
                email=os.environ.get("ARCHIMAGO_EMAIL", "archimago@spellbook.local"),
                password_hash=hash_password(password),
                role=ROLE_ARCHIMAGO,
                invites_left=999,
            )
            db.add(archimago)
            db.flush()
            invite = Invite(code=secrets.token_urlsafe(9), created_by_id=archimago.id)
            db.add(invite)
            print(f"[+] Archimago creado: {username}")
            if not os.environ.get("ARCHIMAGO_PASSWORD"):
                print(f"[!] Contraseña generada (guárdala): {password}")
            print(f"[+] Primera invitación: {invite.code}")
        else:
            print(f"[=] El Archimago '{username}' ya existe")

        db.commit()
        print(f"[+] Grimorio sembrado: {len(SCHOOLS)} escuelas, {len(ARTIFACTS)} artefactos, {len(SPELLS)} hechizos")
    finally:
        db.close()


if __name__ == "__main__":
    main()
