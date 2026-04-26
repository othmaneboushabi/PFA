"""Schémas Pydantic pour les endpoints de traduction.

Ces schémas définissent le format des requêtes et réponses API,
utilisés pour la validation et la génération de la doc Swagger.
"""
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Requête de traduction."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Texte à traduire (max 5000 caractères)",
        examples=[
            "Bonjour, comment allez-vous ?",
            "Hello, how are you?",
        ],
    )
    src_lang: str = Field(
        ...,
        description="Code langue source (fr, en, es, ar)",
        examples=["fr", "en", "es", "ar"],
    )
    tgt_lang: str = Field(
        ...,
        description="Code langue cible (fr, en, es, ar)",
        examples=["fr", "en", "es", "ar"],
    )
    use_cache: bool = Field(
        default=True,
        description="Utiliser le cache Redis (défaut: True)",
    )


class TranslationResponse(BaseModel):
    """Réponse complète d'une traduction."""

    original_text: str = Field(..., description="Texte source")
    translated_text: str = Field(..., description="Texte traduit")
    src_lang: str = Field(..., description="Code langue source")
    tgt_lang: str = Field(..., description="Code langue cible")
    from_cache: bool = Field(
        ...,
        description="True si la traduction provient du cache Redis",
    )
    char_count: int = Field(..., description="Nombre de caractères traduits")