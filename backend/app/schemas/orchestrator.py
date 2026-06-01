"""Schémas Pydantic pour l'orchestrateur."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProcessAudioRequest(BaseModel):
    """Requête de traitement audio complet."""
    
    source_lang: str = Field(
        default="fr",
        description="Langue source de l'audio",
    )
    target_lang: str = Field(
        default="en",
        description="Langue cible pour la traduction",
    )
    extract_entities: bool = Field(
        default=True,
        description="Activer l'extraction d'entités (NER)",
    )
    translate: bool = Field(
        default=True,
        description="Activer la traduction",
    )
    enrich_glossary: bool = Field(
        default=True,
        description="Enrichir avec les glossaires",
    )


class ProcessAudioResponse(BaseModel):
    """Réponse complète du pipeline orchestré."""
    
    audio_file: str
    source_lang: str
    target_lang: str
    transcription: Dict[str, Any]
    entities: Optional[List[Dict[str, Any]]] = None
    translation: Optional[Dict[str, Any]] = None
    glossary_matches: Optional[List[Dict[str, Any]]] = None