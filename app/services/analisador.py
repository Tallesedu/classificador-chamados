import json
import re
import time

from fastapi import HTTPException, status

from app.services import llm_client
from app.schemas.chamado import ChamadoInput
from app.schemas.resposta import AnaliseSentimentoResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

_SYSTEM = """Você é um especialista em atendimento ao cliente e análise emocional.
Analise chamados de suporte de TI e sugira como o atendente deve responder.
Responda APENAS com JSON válido, sem markdown, sem texto extra."""

_SENTIMENTOS = "frustrado, urgente, neutro, satisfeito"


def _build_prompt(chamado: ChamadoInput) -> str:
    return f"""Analise o sentimento do chamado de TI abaixo e sugira uma resposta para o atendente.

Título: {chamado.titulo}
Descrição: {chamado.descricao}

Sentimentos possíveis: {_SENTIMENTOS}

Responda SOMENTE com este JSON (sem markdown):
{{
  "sentimento": "<um dos sentimentos listados>",
  "confianca": <0.0 a 1.0>,
  "tom_detectado": "<descrição do tom em 1 frase>",
  "abordagem_sugerida": "<como o atendente deve agir em 1-2 frases>",
  "resposta_sugerida": "<texto completo da resposta sugerida ao usuário>"
}}"""


def _parse(raw: str) -> AnaliseSentimentoResponse:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JSON não encontrado na resposta da LLM: {raw[:200]}",
        )
    try:
        data = json.loads(match.group())
        return AnaliseSentimentoResponse(**data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao parsear resposta da LLM: {exc}",
        ) from exc


async def analisar(chamado: ChamadoInput) -> AnaliseSentimentoResponse:
    start = time.perf_counter()
    raw = await llm_client.chat(_build_prompt(chamado), system=_SYSTEM)
    elapsed = time.perf_counter() - start
    logger.info("LLM respondeu em %.2fs | titulo=%r", elapsed, chamado.titulo)
    return _parse(raw)
