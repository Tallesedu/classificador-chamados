from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import HTTPException, status

from app.core.config import settings


def _hash(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))


_MOCK_USERS: dict[str, dict[str, Any]] = {
    "admin": {
        "username": "admin",
        "password_hash": _hash("admin123"),
        "role": "admin",
    },
    "user": {
        "username": "user",
        "password_hash": _hash("user123"),
        "role": "user",
    },
}


def authenticate_user(username: str, password: str) -> dict[str, Any]:
    user = _MOCK_USERS.get(username)
    if user is None or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha inválidos.")
    return user


def create_access_token(user: dict[str, Any]) -> tuple[str, int]:
    expires_in = settings.jwt_expiration_minutes * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user["username"],
        "role": user["role"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
        "iss": "classificador-chamados-ti",
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_in


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado.") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.") from exc
