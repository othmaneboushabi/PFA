"""Schémas Pydantic pour le résumé automatique."""
from typing import Optional, List, Union
from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    """Requête de résumé."""
    
    text: str = Field(
        ...,
        min_length=1,
        description="Texte à résumer",
    )
    num_points: int = Field(
        default=5,
        ge=3,
        le=10,
        description="Nombre de points dans le résumé (3-10)",
    )
    focus: Optional[str] = Field(
        default=None,
        description="Focus optionnel (ex: 'key decisions', 'action items')",
    )


class SummarizeResponse(BaseModel):
    """Réponse de résumé."""
    
    summary: Union[List[str], str] = Field(
        ...,
        description="Résumé sous forme de liste de points ou texte brut",
    )
    word_count: int = Field(
        ...,
        description="Nombre de mots du texte original",
    )
    num_points: int = Field(
        ...,
        description="Nombre de points générés (0 si pas résumé)",
    )
    summarized: bool = Field(
        ...,
        description="True si le texte a été résumé",
    )
    original_length: Optional[int] = Field(
        None,
        description="Longueur en caractères du texte original",
    )
    compression_ratio: Optional[float] = Field(
        None,
        description="Ratio de compression (résumé/original)",
    )