import time
from fastapi import APIRouter
from app.schemas.chamado import ChamadoInput
from app.schemas.resposta import ClassificacaoResponse
from app.services import classificador
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/classificar",
    response_model=ClassificacaoResponse,
    summary="Classifica um chamado de TI",
    description=(
        "Recebe título e descrição de um chamado e retorna categoria, "
        "subcategoria, prioridade e justificativa gerados pela LLM."
    ),
)
async def classificar_chamado(chamado: ChamadoInput) -> ClassificacaoResponse:
    start = time.perf_counter()
    logger.info("POST /classificar | titulo=%r", chamado.titulo)
    resultado = await classificador.classificar(chamado)
    logger.info(
        "POST /classificar concluído em %.2fs | categoria=%s | prioridade=%s",
        time.perf_counter() - start,
        resultado.categoria,
        resultado.prioridade,
    )
    return resultado
