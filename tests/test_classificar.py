from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

HEADERS = {"X-API-Key": settings.api_key}

_MOCK_RESPONSE = """{
  "categoria": "Rede",
  "subcategoria": "Conectividade",
  "prioridade": "Alta",
  "justificativa": "Múltiplos usuários afetados em setor crítico."
}"""

_VALID_PAYLOAD = {
    "titulo": "Internet não funciona no 3º andar",
    "descricao": "Desde ontem à tarde nenhum computador consegue acessar a internet.",
}


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_classificar_valido(client):
    with patch("app.services.llm_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = _MOCK_RESPONSE
        resp = client.post("/api/v1/classificar", json=_VALID_PAYLOAD, headers=HEADERS)

    assert resp.status_code == 200
    data = resp.json()
    assert data["categoria"] == "Rede"
    assert data["subcategoria"] == "Conectividade"
    assert data["prioridade"] == "Alta"
    assert "justificativa" in data


def test_classificar_sem_api_key(client):
    resp = client.post("/api/v1/classificar", json=_VALID_PAYLOAD)
    assert resp.status_code == 401


def test_classificar_api_key_invalida(client):
    resp = client.post(
        "/api/v1/classificar",
        json=_VALID_PAYLOAD,
        headers={"X-API-Key": "chave-errada"},
    )
    assert resp.status_code == 401


def test_classificar_titulo_curto(client):
    payload = {"titulo": "Ok", "descricao": "Descrição longa o suficiente para passar."}
    resp = client.post("/api/v1/classificar", json=payload, headers=HEADERS)
    assert resp.status_code == 422


def test_classificar_descricao_curta(client):
    payload = {"titulo": "Título válido aqui", "descricao": "curta"}
    resp = client.post("/api/v1/classificar", json=payload, headers=HEADERS)
    assert resp.status_code == 422


def test_classificar_campos_ausentes(client):
    resp = client.post("/api/v1/classificar", json={}, headers=HEADERS)
    assert resp.status_code == 422


def test_classificar_llm_indisponivel(client):
    from app.exceptions.handlers import LLMUnavailableError

    with patch("app.services.llm_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.side_effect = LLMUnavailableError("Ollama offline")
        resp = client.post("/api/v1/classificar", json=_VALID_PAYLOAD, headers=HEADERS)

    assert resp.status_code == 503


def test_classificar_llm_parsing_error(client):
    from app.exceptions.handlers import LLMParsingError

    with patch("app.services.llm_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "resposta inválida sem json"
        resp = client.post("/api/v1/classificar", json=_VALID_PAYLOAD, headers=HEADERS)

    assert resp.status_code == 500
