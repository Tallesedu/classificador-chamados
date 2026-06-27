from fastapi import APIRouter
from app.schemas.chamado import ChamadoInput
from app.schemas.resposta import AnaliseSentimentoResponse
from app.services import analisador

router = APIRouter()


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
    return await analisador.analisar(chamado)
