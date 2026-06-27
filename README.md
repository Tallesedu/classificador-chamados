# Classificador de Chamados de TI

API REST construída com **FastAPI** que utiliza LLM (Ollama local ou Groq API) para:

- **Classificar** chamados de suporte de TI automaticamente (categoria, prioridade, justificativa)
- **Analisar** o sentimento do chamado e gerar sugestão de resposta para o atendente

A autenticação é feita via **JWT**: o cliente faz `POST /api/v1/auth/login` com usuário e senha e recebe um token Bearer que deve ser enviado nas demais chamadas.

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
# Edite .env com seus valores (JWT_SECRET, LLM_PROVIDER, etc.)
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
| `JWT_SECRET` | `dev-secret-change-in-production` | Segredo usado para assinar/verificar tokens JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura do JWT |
| `JWT_EXPIRATION_MINUTES` | `60` | Tempo de validade do token (1 a 1440 min) |
| `APP_ENV` | `development` | Ambiente |
| `LOG_LEVEL` | `INFO` | Nível de log |

### Ollama local (padrão)

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
JWT_SECRET=troque-em-producao
JWT_EXPIRATION_MINUTES=60
```

### Groq (nuvem — sem custo no plano gratuito)

Crie sua chave em [console.groq.com/keys](https://console.groq.com/keys).

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
JWT_SECRET=troque-em-producao
JWT_EXPIRATION_MINUTES=60
```

Modelos disponíveis na Groq: `llama-3.3-70b-versatile`, `llama3-8b-8192`, `mixtral-8x7b-32768`.

> **Dica:** gere um `JWT_SECRET` forte com `openssl rand -hex 32` ou `python -c "import secrets; print(secrets.token_hex(32))"`.

---

## Execução

```bash
uvicorn app.main:app --reload
```

Acesse a documentação interativa em: **http://localhost:8000/docs**

No Swagger, clique em **Authorize**, cole o `access_token` retornado por `/api/v1/auth/login` e pronto — todas as rotas privadas passam a aceitar a autenticação.

---

## Autenticação

A API protege todas as rotas (exceto `/`, `/docs`, `/redoc`, `/openapi.json` e o próprio `/auth/login`) com **JWT Bearer**.

### Usuários mockados

| Usuário | Senha     | Role    |
|---------|-----------|---------|
| `admin` | `admin123` | `admin` |
| `user`  | `user123`  | `user`  |

> Esses usuários ficam **em memória** com senhas hashadas via **bcrypt** — servem apenas para fins didáticos.

### Fluxo

1. Cliente envia credenciais → `POST /api/v1/auth/login`.
2. API valida e devolve um JWT (`HS256`, claims `sub`, `role`, `iat`, `exp`, `iss`).
3. Cliente envia o token nas chamadas seguintes em `Authorization: Bearer <token>`.
4. Middleware decodifica o token, valida assinatura e expiração e libera a request.

### `POST /api/v1/auth/login`

Autentica o usuário e devolve o token de acesso.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Erros:**
- `401` — usuário ou senha inválidos (mensagem genérica para evitar enumeração).
- `422` — payload inválido (username/senha fora dos limites ou ausentes).

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Validações do payload de login

| Campo | Regras |
|---|---|
| `username` | 3–50 chars, apenas `A-Z`, `a-z`, `0-9`, `_`, `.`, `-` |
| `password` | 6–128 chars |

---

## Endpoints

> Todas as rotas abaixo exigem `Authorization: Bearer <token>` obtido em `/api/v1/auth/login`.

### `POST /api/v1/classificar`

Classifica um chamado de TI.

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
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)

curl -X POST http://localhost:8000/api/v1/classificar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Internet não funciona", "descricao": "Sem acesso desde ontem no setor financeiro."}'
```

---

### `POST /api/v1/analisar`

Analisa sentimento e gera sugestão de resposta.

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
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Sistema lento demais", "descricao": "O sistema está extremamente lento, não consigo trabalhar."}'
```

---

## Estrutura do Projeto

```
app/
├── main.py                    # FastAPI app, CORS, lifespan, OpenAPI BearerAuth
├── api/v1/
│   ├── router.py              # Agrupa rotas v1 (auth, classificar, analisar)
│   └── routes/
│       ├── auth.py            # POST /api/v1/auth/login
│       ├── classificar.py     # POST /api/v1/classificar
│       └── analisar.py        # POST /api/v1/analisar
├── schemas/
│   ├── auth.py                # LoginRequest, TokenResponse
│   ├── chamado.py             # Input: ChamadoInput
│   └── resposta.py            # Output: enums + response models
├── services/
│   ├── auth.py                # Autenticação mockada + bcrypt + JWT
│   ├── llm_client.py          # Cliente HTTP unificado (Ollama/Groq)
│   ├── classificador.py       # Prompt + normalização + parsing de classificação
│   └── analisador.py          # Prompt + parsing de sentimento
├── core/
│   ├── config.py              # Settings via pydantic-settings
│   ├── logging.py             # Logging estruturado
│   └── security.py            # Middleware JWT Bearer
└── exceptions/
    └── handlers.py            # Handler global de erros de validação
```

---

## Códigos de Erro

| Código | Situação |
|---|---|
| 401 | Credenciais inválidas no login, token ausente, expirado, com assinatura inválida ou esquema diferente de `Bearer` |
| 422 | Dados de entrada inválidos (login, título ou descrição fora das regras de validação) |
| 500 | Falha no parsing da resposta da LLM |
| 503 | LLM indisponível (Ollama offline, Groq inacessível, timeout) |

---

## Segurança — resumo

- Senhas armazenadas apenas como hash **bcrypt** (12 rounds).
- Mensagem genérica (`Usuário ou senha inválidos.`) tanto para usuário inexistente quanto para senha errada.
- Token JWT assinado com **HS256**, contendo `sub`, `role`, `iat`, `exp`, `iss`; validação exige claims obrigatórios.
- Header `WWW-Authenticate: Bearer` em respostas 401.
- Rotas públicas explicitamente listadas no middleware (allowlist, não denylist).
- `JWT_SECRET` parametrizado via `.env` e marcado para troca obrigatória em produção.
