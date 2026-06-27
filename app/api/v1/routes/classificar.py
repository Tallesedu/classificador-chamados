from fastapi import APIRouter
from app.schemas.chamado import ChamadoInput
from app.schemas.resposta import ClassificacaoResponse
from app.services import classificador

router = APIRouter()


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
    return await classificador.classificar(chamado)
