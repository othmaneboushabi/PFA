"""Configuration centralisée de l'application AIS.

Charge automatiquement les variables depuis le fichier .env
et les expose comme propriétés typées via Pydantic Settings.

Usage :
    from app.core.config import settings
    print(settings.app_name)
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres globaux de l'application AIS.

    Chaque attribut correspond à une variable d'environnement
    (insensible à la casse) chargée depuis le fichier .env.
    """

    # ========== Application ==========
    app_name: str = "AIS"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True

    # ========== API Server ==========
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # ========== CORS ==========
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # ========== Base de données ==========
    database_url: str = "postgresql+asyncpg://ais_user:ais_password@localhost:5432/ais_db"
    database_url_sync: str = "postgresql://ais_user:ais_password@localhost:5432/ais_db"

    # ========== ASR (faster-whisper) ==========
    whisper_model: str = "small"
    whisper_device: str = "cuda"
    whisper_compute_type: str = "int8"
    whisper_language: str = "auto"

    # ========== Logging ==========
    log_level: str = "INFO"
    log_format: str = "console"
    log_file: str = "logs/ais.log"

    # ========== Sessions ==========
    session_max_duration_hours: int = 4
    transcription_buffer_seconds: int = 3

    # ========== Paths (calculés) ==========
    base_dir: Path = Path(__file__).resolve().parent.parent.parent

    # ========== Configuration Pydantic ==========
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Retourne les origines CORS sous forme de liste Python."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Retourne True si l'environnement est production."""
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Retourne les settings (mis en cache avec lru_cache).

    L'utilisation de lru_cache garantit que les settings ne sont
    lus qu'une seule fois depuis le .env, ce qui évite des I/O disque
    inutiles à chaque requête.
    """
    return Settings()


# Instance globale à importer depuis les autres modules
settings = get_settings()