from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_.-]+$",
        examples=["admin"],
        description="Identificador do usuário (apenas letras, números, '.', '_' e '-').",
    )
    password: str = Field(
        min_length=6,
        max_length=128,
        examples=["admin123"],
        description="Senha do usuário.",
    )


class TokenResponse(BaseModel):
    access_token: str = Field(description="JWT a ser enviado no header Authorization: Bearer.")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(description="Tempo de validade do token em segundos.")
