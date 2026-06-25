from enum import Enum
from pydantic import BaseModel, Field


class Categoria(str, Enum):
    rede = "Rede"
    hardware = "Hardware"
    software = "Software"
    acesso = "Acesso"
    seguranca = "Segurança"
    banco_de_dados = "Banco de Dados"
    outros = "Outros"


class Prioridade(str, Enum):
    critica = "Crítica"
    alta = "Alta"
    media = "Média"
    baixa = "Baixa"


class Sentimento(str, Enum):
    frustrado = "frustrado"
    urgente = "urgente"
    neutro = "neutro"
    satisfeito = "satisfeito"


class ClassificacaoResponse(BaseModel):
    categoria: Categoria
    subcategoria: str
    prioridade: Prioridade
    justificativa: str


class AnaliseSentimentoResponse(BaseModel):
    sentimento: Sentimento
    confianca: float = Field(ge=0.0, le=1.0)
    tom_detectado: str
    abordagem_sugerida: str
    resposta_sugerida: str
