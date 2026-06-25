from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi

from app.core.logging import setup_logging, get_logger
from app.core.security import APIKeyMiddleware
from app.api.v1.router import router as v1_router
from app.exceptions.handlers import (
    LLMUnavailableError,
    LLMParsingError,
    llm_unavailable_handler,
    llm_parsing_handler,
    validation_error_handler,
)

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Classificador de Chamados de TI iniciando...")
    yield
    logger.info("Classificador de Chamados de TI encerrando.")


app = FastAPI(
    title="Classificador de Chamados de TI",
    description=(
        "API que usa LLM para classificar chamados de suporte de TI "
        "e analisar sentimento com sugestão de resposta."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["ApiKeyAuth"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
    }
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            operation.setdefault("security", [{"ApiKeyAuth": []}])
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

# Middlewares
app.add_middleware(APIKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(LLMUnavailableError, llm_unavailable_handler)
app.add_exception_handler(LLMParsingError, llm_parsing_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)

# Rotas
app.include_router(v1_router)


@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok", "docs": "/docs"}
