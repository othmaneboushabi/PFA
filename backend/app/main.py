"""Point d'entrée principal de l'application FastAPI AIS.

Ce module :
    - Crée l'instance FastAPI
    - Configure le cycle de vie (startup/shutdown)
    - Active les middlewares (CORS, logging, etc.)
    - Enregistre toutes les routes

Lancement en développement :
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Documentation interactive :
    http://localhost:8000/docs      (Swagger UI)
    http://localhost:8000/redoc     (ReDoc)
"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import health, ner, transcription, translation
from app.core.config import settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Gère le cycle de vie de l'application.

    Le code AVANT le yield s'exécute au démarrage.
    Le code APRÈS le yield s'exécute à l'arrêt.
    """
    # ===== STARTUP =====
    setup_logging()
    logger.info("=" * 70)
    logger.info(f"🚀 Démarrage de {settings.app_name} v{settings.app_version}")
    logger.info(f"   Environnement : {settings.app_env}")
    logger.info(
        f"   Whisper       : modèle={settings.whisper_model} | "
        f"device={settings.whisper_device} | "
        f"compute={settings.whisper_compute_type}"
    )
    logger.info(f"   API           : http://{settings.api_host}:{settings.api_port}")
    logger.info(f"   Docs          : http://localhost:{settings.api_port}/docs")
    logger.info("=" * 70)

    yield

    # ===== SHUTDOWN =====
    logger.info("👋 Arrêt propre de l'application AIS")


# ===== Création de l'application FastAPI =====
app = FastAPI(
    title=f"{settings.app_name} API",
    description=(
        "**Assistant Interprète Simultané** — "
        "API REST et WebSocket pour l'assistance temps réel aux interprètes. "
        "Stack : FastAPI + faster-whisper + spaCy + Gemma 4."
    ),
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ===== Middleware CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Enregistrement des routes =====
app.include_router(
    health.router,
    prefix=settings.api_prefix,
    tags=["Health"],
)
app.include_router(
    transcription.router,
    prefix=settings.api_prefix,
    tags=["Transcription"],
)
app.include_router(
    ner.router,
    prefix=settings.api_prefix,
    tags=["NER"],
)
app.include_router(
    translation.router,
    prefix=settings.api_prefix,
    tags=["Translation"],
)
# ===== Route racine =====
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Page d'accueil de l'API avec liens vers les ressources principales."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": f"{settings.api_prefix}/health",
    }