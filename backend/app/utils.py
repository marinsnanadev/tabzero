import secrets

from slugify import slugify
from sqlalchemy.orm import Session as DBSession

from app import models


def generate_unique_slug(db: DBSession, name: str) -> str:
    """
    Gera um slug a partir do nome da sessão, adicionando um sufixo aleatório
    curto para evitar colisões e tornar o link não-adivinhável por terceiros
    (ex: "viagem-praia-2024" vira "viagem-praia-2024-a1b2c3").
    """
    base_slug = slugify(name) or "sessao"

    for _ in range(5):
        suffix = secrets.token_hex(3)  # 6 caracteres hex
        candidate = f"{base_slug}-{suffix}"
        exists = (
            db.query(models.Session).filter(models.Session.slug == candidate).first()
        )
        if not exists:
            return candidate

    # fallback extremamente improvável de acontecer
    return f"{base_slug}-{secrets.token_hex(8)}"
