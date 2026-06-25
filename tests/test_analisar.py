from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

HEADERS = {"X-API-Key": settings.api_key}

_MOCK_RESPONSE = """{
  "sentimento": "frustrado",
  "confianca": 0.95,
  "tom_detectado": "Usuário demonstra frustração acumulada.",
  "abordagem_sugerida": "Demonstrar empatia e dar prazo concreto.",
  "resposta_sugerida": "Olá, compreendo sua frustração. Vou tratar com prioridade."
}"""

_VALID_PAYLOAD = {
    "titulo": "URGENTE - Sistema travou de novo!!!",
    "descricao": "Pelo amor de Deus, é a terceira vez essa semana que o sistema trava.",
}


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_analisar_valido(client):
    with patch("app.services.llm_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = _MOCK_RESPONSE
        resp = client.post("/api/v1/analisar", json=_VALID_PAYLOAD, headers=HEADERS)

    assert resp.status_code == 200
    data = resp.json()
    assert data["sentimento"] == "frustrado"
    assert 0.0 <= data["confianca"] <= 1.0
    assert "tom_detectado" in data
    assert "abordagem_sugerida" in data
    assert "resposta_sugerida" in data


def test_analisar_sem_api_key(client):
    resp = client.post("/api/v1/analisar", json=_VALID_PAYLOAD)
    assert resp.status_code == 401


def test_analisar_api_key_invalida(client):
    resp = client.post(
        "/api/v1/analisar",
        json=_VALID_PAYLOAD,
        headers={"X-API-Key": "chave-errada"},
    )
    assert resp.status_code == 401


def test_analisar_titulo_curto(client):
    payload = {"titulo": "Ok", "descricao": "Descrição longa o suficiente para o teste."}
    resp = client.post("/api/v1/analisar", json=payload, headers=HEADERS)
    assert resp.status_code == 422


def test_analisar_campos_ausentes(client):
    resp = client.post("/api/v1/analisar", json={"titulo": "Somente título"}, headers=HEADERS)
    assert resp.status_code == 422


def test_analisar_llm_indisponivel(client):
    from app.exceptions.handlers import LLMUnavailableError

    with patch("app.services.llm_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.side_effect = LLMUnavailableError("Ollama offline")
        resp = client.post("/api/v1/analisar", json=_VALID_PAYLOAD, headers=HEADERS)

    assert resp.status_code == 503


def test_analisar_llm_parsing_error(client):
    with patch("app.services.llm_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "texto sem json válido"
        resp = client.post("/api/v1/analisar", json=_VALID_PAYLOAD, headers=HEADERS)

    assert resp.status_code == 500


def test_docs_acessivel_sem_autenticacao(client):
    resp = client.get("/docs")
    assert resp.status_code == 200
