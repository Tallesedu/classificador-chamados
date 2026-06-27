from fastapi import APIRouter
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth as auth_service

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autentica usuário e retorna token JWT",
    description=(
        "Recebe `username` e `password`, valida contra a base mockada e retorna "
        "um JWT a ser enviado em chamadas subsequentes via header "
        "`Authorization: Bearer <token>`."
    ),
    responses={
        200: {"description": "Login bem-sucedido."},
        401: {"description": "Credenciais inválidas."},
        422: {"description": "Dados de entrada inválidos."},
    },
)
async def login(credentials: LoginRequest) -> TokenResponse:
    user = auth_service.authenticate_user(credentials.username, credentials.password)
    token, expires_in = auth_service.create_access_token(user)
    return TokenResponse(access_token=token, expires_in=expires_in)
