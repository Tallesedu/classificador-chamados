import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_GROQ_BASE_URL = "https://api.groq.com/openai"
_CHAT_PATH = "/v1/chat/completions"


def _build_headers() -> dict:
    if settings.llm_provider == "groq":
        if not settings.groq_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GROQ_API_KEY não configurada no .env",
            )
        return {"Authorization": f"Bearer {settings.groq_api_key}"}
    return {}


def _base_url() -> str:
    if settings.llm_provider == "groq":
        return _GROQ_BASE_URL
    return settings.llm_base_url.rstrip("/")


async def chat(prompt: str, system: str = "") -> str:
    url = _base_url() + _CHAT_PATH
    headers = _build_headers()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "stream": False,
        "temperature": 0,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("Erro ao chamar LLM em %s: %s", url, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de LLM indisponível. Verifique se o Ollama está rodando.",
        ) from exc

    return response.json()["choices"][0]["message"]["content"]


async def health_check() -> bool:
    try:
        await chat("Responda apenas: OK")
        return True
    except HTTPException:
        return False
