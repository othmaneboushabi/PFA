"""Configuration de la base de données PostgreSQL.

Utilise SQLAlchemy avec AsyncIO pour compatibilité FastAPI.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base
from loguru import logger

from app.core.config import settings

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Moteur async PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Mettre True pour voir les requêtes SQL (debug)
    pool_pre_ping=True,  # Vérifie la connexion avant utilisation
    pool_size=5,
    max_overflow=10,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Dependency pour obtenir une session de base de données.
    
    Usage dans les routes FastAPI :
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialise la base de données (crée les tables)."""
    async with engine.begin() as conn:
        # Créer toutes les tables définies dans Base.metadata
        await conn.run_sync(Base.metadata.create_all)
    
    logger.success("✅ Tables PostgreSQL créées")


async def close_db():
    """Ferme les connexions à la base de données."""
    await engine.dispose()
    logger.info("🔒 Connexions PostgreSQL fermées")