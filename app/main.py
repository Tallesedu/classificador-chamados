from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi

from app.core.logging import setup_logging, get_logger
from app.core.security import JWTAuthMiddleware
from app.api.v1.router import router as v1_router
from app.exceptions.handlers import validation_error_handler

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
        "e analisar sentimento com sugestão de resposta. "
        "Autenticação via JWT obtido em `POST /api/v1/auth/login`."
    ),
    version="1.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


_PUBLIC_OPERATION_PATHS = {"/api/v1/auth/login"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    for path, methods in schema.get("paths", {}).items():
        for operation in methods.values():
            if path in _PUBLIC_OPERATION_PATHS:
                operation["security"] = []
            else:
                operation.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(JWTAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_error_handler)

app.include_router(v1_router)


@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok", "docs": "/docs"}
