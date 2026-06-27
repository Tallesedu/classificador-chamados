import json
import re
import time

from fastapi import HTTPException, status

from app.services import llm_client
from app.schemas.chamado import ChamadoInput
from app.schemas.resposta import ClassificacaoResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

_SYSTEM = """Você é um especialista em suporte de TI. Classifique chamados técnicos.
Responda APENAS com JSON válido, sem markdown, sem texto extra."""

_CATEGORIA_MAP = {
    "rede": "Rede",
    "hardware": "Hardware",
    "software": "Software",
    "acesso": "Acesso",
    "segurança": "Segurança",
    "seguranca": "Segurança",
    "banco de dados": "Banco de Dados",
    "banco": "Banco de Dados",
    "database": "Banco de Dados",
    "outros": "Outros",
    "other": "Outros",
}

_PRIORIDADE_MAP = {
    "crítica": "Crítica",
    "critica": "Crítica",
    "critical": "Crítica",
    "alta": "Alta",
    "high": "Alta",
    "média": "Média",
    "media": "Média",
    "medium": "Média",
    "baixa": "Baixa",
    "low": "Baixa",
}


def _build_prompt(chamado: ChamadoInput) -> str:
    return f"""Classifique o chamado de TI abaixo.

Título: {chamado.titulo}
Descrição: {chamado.descricao}

REGRAS ESTRITAS — use EXATAMENTE os valores indicados:

"categoria" deve ser uma destas 7 opções (copie exatamente):
  Rede | Hardware | Software | Acesso | Segurança | Banco de Dados | Outros

  - Rede: internet, VPN, firewall, conectividade, roteador
  - Hardware: impressora, monitor, periféricos, equipamento físico
  - Software: instalação, atualização, erro de aplicação, licença
  - Acesso: permissão, conta, senha, e-mail, login
  - Segurança: vírus, phishing, vazamento, bloqueio de segurança
  - Banco de Dados: lentidão, erro ou backup de banco de dados
  - Outros: não se enquadra nas anteriores

"subcategoria" deve ser uma palavra ou termo curto dentro da categoria (ex: VPN, Impressora, Senha, Vírus).

"prioridade" deve ser uma destas 4 opções (copie exatamente):
  Crítica | Alta | Média | Baixa

  - Crítica: sistema fora do ar, múltiplos usuários impactados
  - Alta: funcionalidade importante comprometida
  - Média: inconveniente, existe solução alternativa
  - Baixa: dúvida, solicitação ou melhoria

"justificativa" deve ser 1 a 2 frases explicando a classificação.

Responda SOMENTE com este JSON (sem markdown, sem texto antes ou depois):
{{"categoria": "<uma das 7 categorias>", "subcategoria": "<subcategoria específica>", "prioridade": "<uma das 4 prioridades>", "justificativa": "<1-2 frases>"}}"""


def _normalizar(data: dict) -> dict:
    cat = data.get("categoria", "").lower().strip()
    data["categoria"] = _CATEGORIA_MAP.get(cat, next(
        (v for k, v in _CATEGORIA_MAP.items() if cat.startswith(k)), data["categoria"]
    ))

    pri = data.get("prioridade", "").lower().strip()
    data["prioridade"] = _PRIORIDADE_MAP.get(pri, next(
        (v for k, v in _PRIORIDADE_MAP.items() if pri.startswith(k)), data["prioridade"]
    ))
    return data


def _parse(raw: str) -> ClassificacaoResponse:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JSON não encontrado na resposta da LLM: {raw[:200]}",
        )
    try:
        data = json.loads(match.group())
        data = _normalizar(data)
        return ClassificacaoResponse(**data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao parsear resposta da LLM: {exc}",
        ) from exc


async def classificar(chamado: ChamadoInput) -> ClassificacaoResponse:
    start = time.perf_counter()
    raw = await llm_client.chat(_build_prompt(chamado), system=_SYSTEM)
    elapsed = time.perf_counter() - start
    logger.info("LLM respondeu em %.2fs | titulo=%r", elapsed, chamado.titulo)
    return _parse(raw)
