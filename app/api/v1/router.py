from fastapi import APIRouter
from app.api.v1.routes import analisar, auth, classificar

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
router.include_router(classificar.router, tags=["Classificação"])
router.include_router(analisar.router, tags=["Análise de Sentimento"])
