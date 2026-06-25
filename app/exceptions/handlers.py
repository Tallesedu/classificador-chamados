from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class LLMUnavailableError(Exception):
    """LLM inacessível (Ollama offline, Groq indisponível, timeout)."""


class LLMParsingError(Exception):
    """Falha ao fazer parsing da resposta da LLM."""


async def llm_unavailable_handler(request: Request, exc: LLMUnavailableError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Serviço de LLM indisponível. Verifique se o Ollama está rodando.",
            "error": str(exc),
        },
    )


async def llm_parsing_handler(request: Request, exc: LLMParsingError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Falha ao interpretar resposta da LLM.",
            "error": str(exc),
        },
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " → ".join(str(loc) for loc in err["loc"])
        errors.append({"campo": field, "mensagem": err["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Dados de entrada inválidos.", "erros": errors},
    )
