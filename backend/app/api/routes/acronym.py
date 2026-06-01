"""Routes pour l'extraction et l'explication d'acronymes."""
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.schemas.acronym import (
    ExplainAcronymRequest,
    AcronymExplanation,
    ProcessTextRequest,
    ProcessTextResponse,
)
from app.services.acronym_service import get_acronym_service

router = APIRouter()


@router.post(
    "/acronyms/explain",
    response_model=AcronymExplanation,
    summary="Expliquer un acronyme",
    description=(
        "Explique un acronyme en cherchant d'abord dans les glossaires, "
        "puis via Gemma 2 si absent."
    ),
    status_code=status.HTTP_200_OK,
)
async def explain_acronym(request: ExplainAcronymRequest) -> AcronymExplanation:
    """Explique un acronyme unique."""
    
    logger.info(f"🔍 Requête explication : '{request.acronym}'")
    
    try:
        acronym_service = get_acronym_service()
        result = await acronym_service.explain_acronym(
            acronym=request.acronym,
            context=request.context or "",
            domain=request.domain,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )
        
        return AcronymExplanation(**result)
    
    except RuntimeError as e:
        logger.error(f"❌ Erreur Ollama : {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama non disponible : {str(e)}",
        ) from e
    
    except Exception as e:
        logger.exception(f"❌ Erreur explication acronyme : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur : {str(e)}",
        ) from e


@router.post(
    "/acronyms/process",
    response_model=ProcessTextResponse,
    summary="Extraire et expliquer tous les acronymes d'un texte",
    description=(
        "Détecte automatiquement tous les acronymes dans un texte, "
        "puis explique chacun via glossaires ou Gemma 2."
    ),
    status_code=status.HTTP_200_OK,
)
async def process_text_acronyms(request: ProcessTextRequest) -> ProcessTextResponse:
    """Traite un texte complet pour extraire et expliquer les acronymes."""
    
    logger.info(
        f"📄 Requête traitement texte : {len(request.text)} chars | "
        f"domaine={request.domain or 'auto'}"
    )
    
    try:
        acronym_service = get_acronym_service()
        result = await acronym_service.process_text(
            text=request.text,
            domain=request.domain,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )
        
        return ProcessTextResponse(**result)
    
    except RuntimeError as e:
        logger.error(f"❌ Erreur Ollama : {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama non disponible : {str(e)}",
        ) from e
    
    except Exception as e:
        logger.exception(f"❌ Erreur traitement acronymes : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur : {str(e)}",
        ) from e