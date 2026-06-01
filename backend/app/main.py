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
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import health, ner, transcription, translation, glossary, orchestrator, summarization, acronym,streaming
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_db, close_db



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup
    setup_logging()
    logger.info("======================================================================")
    logger.info(f"🚀 Démarrage de {settings.app_name} v{settings.app_version}")
    logger.info(f"   Environnement : {settings.app_env}")
    logger.info(f"   Whisper       : modèle={settings.whisper_model} | device={settings.whisper_device} | compute={settings.whisper_compute_type}")
    
    # Initialiser la base de données
    await init_db()
    
    logger.info(f"   API           : http://{settings.api_host}:{settings.api_port}")
    logger.info(f"   Docs          : http://localhost:{settings.api_port}/docs")
    logger.info("======================================================================")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arrêt de l'application")
    await close_db()


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

# ===== Fichiers statiques (Frontend) =====
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/ui", include_in_schema=False)
async def serve_frontend():
    return FileResponse("app/static/index.html")

# ===== Enregistrement des routes =====
app.include_router(
    health.router,
    prefix=settings.api_prefix,
    tags=["Health"],
)
# Transcription
app.include_router(
    transcription.router,
    prefix=settings.api_prefix,
    tags=["Transcription"],
)

# NER
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
app.include_router(
    glossary.router,
    prefix=settings.api_prefix,
    tags=["Glossary"],
)
app.include_router(
    orchestrator.router,
    prefix=settings.api_prefix,
    tags=["Orchestrator"],
)
app.include_router(
    summarization.router,
    prefix=settings.api_prefix,
    tags=["Summarization"],
)
app.include_router(
    acronym.router,
    prefix=settings.api_prefix,
    tags=["Acronyms"],
)
# Streaming temps réel
app.include_router(
    streaming.router,
    tags=["Streaming"],
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