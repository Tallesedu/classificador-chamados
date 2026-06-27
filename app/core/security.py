from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger
from app.services import auth as auth_service

logger = get_logger(__name__)

_PUBLIC_PATHS = {
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/login",
}


def _unauthorized(detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": detail},
        headers={"WWW-Authenticate": "Bearer"},
    )


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in _PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.lower().startswith("bearer "):
            logger.warning("401 em %s | motivo=token ausente ou esquema inválido", path)
            return _unauthorized("Token de autenticação ausente. Use 'Authorization: Bearer <token>'.")

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            logger.warning("401 em %s | motivo=token vazio", path)
            return _unauthorized("Token de autenticação vazio.")

        try:
            payload = auth_service.decode_access_token(token)
        except HTTPException as exc:
            logger.warning("401 em %s | motivo=%s", path, exc.detail)
            return _unauthorized(exc.detail)

        request.state.user = payload
        return await call_next(request)
