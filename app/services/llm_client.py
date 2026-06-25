import httpx
from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions.handlers import LLMUnavailableError

logger = get_logger(__name__)

_GROQ_BASE_URL = "https://api.groq.com/openai"
_CHAT_PATH = "/v1/chat/completions"


def _build_headers() -> dict:
    if settings.llm_provider == "groq":
        if not settings.groq_api_key:
            raise LLMUnavailableError("GROQ_API_KEY não configurada no .env")
        return {"Authorization": f"Bearer {settings.groq_api_key}"}
    return {}


def _base_url() -> str:
    if settings.llm_provider == "groq":
        return _GROQ_BASE_URL
    return settings.llm_base_url.rstrip("/")


async def chat(prompt: str, system: str = "") -> str:
    """Envia um prompt para a LLM e retorna o conteúdo da resposta."""
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
    except httpx.ConnectError as exc:
        logger.error("LLM inacessível em %s: %s", url, exc)
        raise LLMUnavailableError(f"Não foi possível conectar ao LLM em {url}") from exc
    except httpx.TimeoutException as exc:
        logger.error("Timeout ao chamar LLM em %s", url)
        raise LLMUnavailableError("Timeout na chamada ao LLM") from exc
    except httpx.HTTPStatusError as exc:
        logger.error("LLM retornou HTTP %s: %s", exc.response.status_code, exc.response.text)
        raise LLMUnavailableError(f"LLM retornou erro HTTP {exc.response.status_code}") from exc

    data = response.json()
    return data["choices"][0]["message"]["content"]


async def health_check() -> bool:
    """Retorna True se a LLM responder ao health check."""
    try:
        await chat("Responda apenas: OK")
        return True
    except LLMUnavailableError:
        return False
