from pydantic import BaseModel, Field


class ChamadoInput(BaseModel):
    titulo: str = Field(
        min_length=5,
        max_length=200,
        examples=["Internet não funciona no 3º andar"],
    )
    descricao: str = Field(
        min_length=10,
        max_length=2000,
        examples=[
            "Desde ontem à tarde nenhum computador do setor financeiro "
            "consegue acessar a internet. Já reiniciamos o roteador."
        ],
    )
