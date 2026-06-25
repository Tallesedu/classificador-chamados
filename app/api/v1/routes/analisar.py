import time
from fastapi import APIRouter
from app.schemas.chamado import ChamadoInput
from app.schemas.resposta import AnaliseSentimentoResponse
from app.services import analisador
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/analisar",
    response_model=AnaliseSentimentoResponse,
    summary="Analisa sentimento de um chamado de TI",
    description=(
        "Recebe título e descrição de um chamado e retorna análise de sentimento "
        "e sugestão de resposta para o atendente, gerados pela LLM."
    ),
)
async def analisar_chamado(chamado: ChamadoInput) -> AnaliseSentimentoResponse:
    start = time.perf_counter()
    logger.info("POST /analisar | titulo=%r", chamado.titulo)
    resultado = await analisador.analisar(chamado)
    logger.info(
        "POST /analisar concluído em %.2fs | sentimento=%s | confianca=%.2f",
        time.perf_counter() - start,
        resultado.sentimento,
        resultado.confianca,
    )
    return resultado
