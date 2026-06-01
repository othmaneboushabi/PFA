"""Schémas Pydantic pour les endpoints de glossaires."""
from typing import Optional, List
from pydantic import BaseModel, Field


class GlossaryUploadResponse(BaseModel):
    """Réponse après upload d'un glossaire."""
    
    glossary_id: str = Field(..., description="ID unique du glossaire")
    glossary_name: str = Field(..., description="Nom du glossaire")
    entries_count: int = Field(..., description="Nombre d'entrées importées")
    format: str = Field(..., description="Format du fichier (csv, json, xlsx, tbx)")


class GlossarySearchRequest(BaseModel):
    """Requête de recherche dans les glossaires."""
    
    term: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Terme à rechercher",
        examples=["OPCVM", "mise en demeure", "VaR"],
    )
    source_lang: str = Field(
        default="fr",
        description="Langue source (fr, en, es, ar)",
        examples=["fr", "en"],
    )
    target_lang: str = Field(
        default="en",
        description="Langue cible (fr, en, es, ar)",
        examples=["en", "es"],
    )
    glossary_id: Optional[str] = Field(
        default=None,
        description="ID du glossaire spécifique (None = chercher dans tous)",
    )
    fuzzy_threshold: int = Field(
        default=80,
        ge=0,
        le=100,
        description="Seuil de correspondance floue (0-100, défaut 80)",
    )


class GlossaryEntryResult(BaseModel):
    """Résultat de recherche d'un terme dans un glossaire."""
    
    glossary_id: str = Field(..., description="ID du glossaire source")
    glossary_name: str = Field(..., description="Nom du glossaire")
    source_term: str = Field(..., description="Terme source")
    target_term: str = Field(..., description="Terme cible (traduction)")
    source_lang: str = Field(..., description="Langue source")
    target_lang: str = Field(..., description="Langue cible")
    context: Optional[str] = Field(None, description="Contexte d'utilisation")
    domain: Optional[str] = Field(None, description="Domaine métier (finance, médical, etc.)")
    match_score: int = Field(..., description="Score de correspondance (0-100)")
    matched_as: str = Field(..., description="Terme exact qui a matché")


class GlossarySearchResponse(BaseModel):
    """Réponse de recherche dans les glossaires."""
    
    query_term: str = Field(..., description="Terme recherché")
    results_count: int = Field(..., description="Nombre de résultats trouvés")
    results: List[GlossaryEntryResult] = Field(
        default=[],
        description="Liste des résultats triés par score",
    )


class GlossaryListItem(BaseModel):
    """Item dans la liste des glossaires."""
    
    glossary_id: str
    glossary_name: str
    entries_count: int
    created_at: str


class GlossaryListResponse(BaseModel):
    """Réponse de listage des glossaires."""
    
    total_glossaries: int
    glossaries: List[GlossaryListItem]