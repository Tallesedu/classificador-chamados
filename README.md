# Classificador de Chamados de TI

API REST construída com **FastAPI** que utiliza LLM (Ollama local ou Groq API) para:

- **Classificar** chamados de suporte de TI automaticamente (categoria, prioridade, justificativa)
- **Analisar** o sentimento do chamado e gerar sugestão de resposta para o atendente

> **Disciplina:** Construção de APIs para Inteligência Artificial — Entrega: 30/06/2026

---

## Pré-requisitos

- Python 3.11+
- **Ollama** instalado e rodando localmente **ou** uma conta na **[Groq](https://console.groq.com)**

```bash
# Ollama — instalar e baixar o modelo (uma vez só)
ollama pull llama3.2
ollama serve          # mantém rodando em background
```

---

## Instalação

```bash
# 1. Clone o repositório
git clone <URL_DO_REPO>
cd classificador-chamados

# 2. Crie e ative o ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com seus valores (API_KEY, LLM_PROVIDER, etc.)
```

---

## Configuração do `.env`

| Variável | Padrão | Descrição |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | Backend: `ollama` (local) ou `groq` (nuvem) |
| `LLM_BASE_URL` | `http://localhost:11434` | URL do Ollama (ignorada no provider groq) |
| `LLM_MODEL` | `llama3.2` | Modelo a ser usado |
| `LLM_TIMEOUT` | `60` | Timeout em segundos |
| `GROQ_API_KEY` | — | Chave da Groq API (obrigatória se `LLM_PROVIDER=groq`) |
| `API_KEY` | — | Chave de autenticação da API (`X-API-Key`) |
| `APP_ENV` | `development` | Ambiente |
| `LOG_LEVEL` | `INFO` | Nível de log |

### Ollama local (padrão)

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
API_KEY=minha-chave-secreta
```

### Groq (nuvem — sem custo no plano gratuito)

Crie sua chave em [console.groq.com/keys](https://console.groq.com/keys).

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
API_KEY=minha-chave-secreta
```

Modelos disponíveis na Groq: `llama-3.3-70b-versatile`, `llama3-8b-8192`, `mixtral-8x7b-32768`.

---

## Execução

```bash
uvicorn app.main:app --reload
```

Acesse a documentação interativa em: **http://localhost:8000/docs**

---

## Endpoints

### `POST /api/v1/classificar`

Classifica um chamado de TI.

**Header obrigatório:** `X-API-Key: <sua-chave>`

**Request:**
```json
{
  "titulo": "Internet não funciona no 3º andar",
  "descricao": "Desde ontem à tarde nenhum computador do setor financeiro consegue acessar a internet."
}
```

**Response:**
```json
{
  "categoria": "Rede",
  "subcategoria": "Conectividade",
  "prioridade": "Alta",
  "justificativa": "Múltiplos usuários afetados em setor crítico."
}
```

```bash
curl -X POST http://localhost:8000/api/v1/classificar \
  -H "X-API-Key: minha-chave-secreta" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Internet não funciona", "descricao": "Sem acesso desde ontem no setor financeiro."}'
```

---

### `POST /api/v1/analisar`

Analisa sentimento e gera sugestão de resposta.

**Header obrigatório:** `X-API-Key: <sua-chave>`

**Request:**
```json
{
  "titulo": "URGENTE - Sistema travou de novo!!!",
  "descricao": "Pelo amor de Deus, é a terceira vez essa semana que o sistema trava."
}
```

**Response:**
```json
{
  "sentimento": "frustrado",
  "confianca": 0.95,
  "tom_detectado": "Frustração acumulada por recorrência do problema.",
  "abordagem_sugerida": "Demonstrar empatia e dar prazo concreto.",
  "resposta_sugerida": "Olá, compreendo sua frustração..."
}
```

```bash
curl -X POST http://localhost:8000/api/v1/analisar \
  -H "X-API-Key: minha-chave-secreta" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Sistema lento demais", "descricao": "O sistema está extremamente lento, não consigo trabalhar."}'
```

---

## Testes

```bash
pytest -v
```

Os testes usam mocks para a LLM — não é necessário ter o Ollama rodando nem a chave Groq configurada.

---

## Estrutura do Projeto

```
app/
├── main.py                    # FastAPI app, CORS, lifespan
├── api/v1/
│   ├── router.py              # Agrupa rotas v1
│   └── routes/
│       ├── classificar.py     # POST /api/v1/classificar
│       └── analisar.py        # POST /api/v1/analisar
├── schemas/
│   ├── chamado.py             # Input: ChamadoInput
│   └── resposta.py            # Output: enums + response models
├── services/
│   ├── llm_client.py          # Cliente HTTP unificado (Ollama/Groq)
│   ├── classificador.py       # Prompt + parsing de classificação
│   └── analisador.py          # Prompt + parsing de sentimento
├── core/
│   ├── config.py              # Settings via pydantic-settings
│   ├── logging.py             # Logging estruturado
│   └── security.py            # Middleware X-API-Key
└── exceptions/
    └── handlers.py            # Exception handlers globais
tests/
├── conftest.py
├── test_classificar.py
└── test_analisar.py
```

---

## Códigos de Erro

| Código | Situação |
|---|---|
| 401 | API Key ausente ou inválida |
| 422 | Dados de entrada inválidos (título/descrição) |
| 500 | Falha no parsing da resposta da LLM |
| 503 | LLM indisponível (Ollama offline, Groq inacessível, timeout) |
