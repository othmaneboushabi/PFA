"""Schémas Pydantic pour l'extraction d'acronymes."""
from typing import Optional, List
from pydantic import BaseModel, Field


class ExplainAcronymRequest(BaseModel):
    """Requête d'explication d'un acronyme unique."""
    
    acronym: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Acronyme à expliquer (ex: 'OPCVM', 'AI', 'NASA')",
    )
    context: Optional[str] = Field(
        default=None,
        description="Contexte optionnel (phrase où apparaît l'acronyme)",
    )
    domain: Optional[str] = Field(
        default=None,
        description="Domaine optionnel (finance, medical, tech, etc.)",
    )
    source_lang: str = Field(
        default="fr",
        description="Langue source",
    )
    target_lang: str = Field(
        default="en",
        description="Langue cible",
    )


class ProcessTextRequest(BaseModel):
    """Requête de traitement complet d'un texte."""
    
    text: str = Field(
        ...,
        min_length=1,
        description="Texte contenant des acronymes",
    )
    domain: Optional[str] = Field(
        default=None,
        description="Domaine optionnel",
    )
    source_lang: str = Field(
        default="fr",
        description="Langue source",
    )
    target_lang: str = Field(
        default="en",
        description="Langue cible",
    )


class AcronymExplanation(BaseModel):
    """Explication d'un acronyme."""
    
    acronym: str
    explanation: str
    full_form: str
    source: str = Field(
        ...,
        description="Source de l'explication : 'glossary' ou 'ai'",
    )
    domain: Optional[str] = None
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confiance dans l'explication (0-1)",
    )
    glossary_id: Optional[str] = Field(
        default=None,
        description="ID du glossaire si source=glossary",
    )


class ProcessTextResponse(BaseModel):
    """Réponse de traitement de texte."""
    
    text: str
    acronyms_found: int
    acronyms: List[AcronymExplanation]
    domain: Optional[str] = None