"""Schémas Pydantic pour les endpoints NER."""
from pydantic import BaseModel, Field


class EntityItem(BaseModel):
    """Une entité nommée détectée dans le texte."""

    text: str = Field(..., description="Texte de l'entité extraite")
    label: str = Field(
        ...,
        description="Catégorie normalisée (PER, ORG, LOC, DATE, NUM, MISC)",
    )
    start: int = Field(..., description="Position de début (index caractère)")
    end: int = Field(..., description="Position de fin (index caractère)")


class NERRequest(BaseModel):
    """Requête d'extraction d'entités nommées."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Texte à analyser (max 50 000 caractères)",
        examples=[
            "Apple a annoncé hier à Cupertino que Tim Cook investira 500 millions de dollars."
        ],
    )
    language: str = Field(
        default="fr",
        description="Code langue (fr, en, es, ar)",
        examples=["fr", "en", "es", "ar"],
    )


class NERResponse(BaseModel):
    """Réponse complète d'une extraction NER."""

    text: str = Field(..., description="Texte analysé")
    language: str = Field(..., description="Code langue utilisé (fr, en, es, ar)")
    entities: list[EntityItem] = Field(
        default_factory=list,
        description="Liste des entités détectées",
    )
    entity_count: int = Field(..., description="Nombre total d'entités détectées")