"""Routes d'extraction d'entités nommées (NER).

Endpoints :
    POST /ner : extraction NER sur un texte fourni

Langues supportées : FR, EN, ES, AR
"""
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.schemas.ner import EntityItem, NERRequest, NERResponse
from app.services.ner_service import get_ner_service

router = APIRouter()

SUPPORTED_LANGUAGES = ["fr", "en", "es", "ar"]

@router.post(
    "/ner",
    response_model=NERResponse,
    summary="Extraction d'entités nommées (NER)",
    description=(
        "Extrait les entités nommées d'un texte via spaCy (FR/EN/ES) "
        "ou HuggingFace CAMeL BERT (AR). "
        "Labels normalisés : PER, ORG, LOC, DATE, NUM, MISC."
    ),
    status_code=status.HTTP_200_OK,
)
async def extract_entities(request: NERRequest) -> NERResponse:
    """Extrait les entités nommées d'un texte donné."""

    logger.info(
        f"📥 Requête NER reçue : langue={request.language}, "
        f"texte={len(request.text)} caractères"
    )

    try:
        # Validation langue
        if request.language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Langue '{request.language}' non supportée. "
                f"Langues disponibles : {', '.join(SUPPORTED_LANGUAGES)}",
            )

        # Extraction NER
        ner_service = get_ner_service()
        entities = ner_service.extract_entities(
            text=request.text,
            language=request.language,
        )

        return NERResponse(
            text=request.text,
            language=request.language,
            entities=[EntityItem(**e) for e in entities],
            entity_count=len(entities),
        )

    except HTTPException:
        raise

    except ValueError as e:
        logger.error(f"❌ Erreur de validation : {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except Exception as e:
        logger.exception(f"❌ Erreur lors de l'extraction NER : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'extraction NER : {str(e)}",
        ) from e