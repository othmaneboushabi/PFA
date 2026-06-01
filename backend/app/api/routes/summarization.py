"""Routes pour le résumé automatique."""
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.schemas.summarization import SummarizeRequest, SummarizeResponse
from app.services.summarization_service import get_summarization_service

router = APIRouter()


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    summary="Résumé automatique de texte",
    description=(
        "Génère un résumé concis d'un texte long via Gemma 2. "
        "Idéal pour résumer des transcriptions de réunions, conférences, etc."
    ),
    status_code=status.HTTP_200_OK,
)
async def summarize_text(request: SummarizeRequest) -> SummarizeResponse:
    """Résume un texte en bullet points."""
    
    logger.info(
        f"📝 Requête résumé : {len(request.text)} chars, "
        f"{request.num_points} points"
    )
    
    try:
        summarization_service = get_summarization_service()
        result = summarization_service.summarize(
            text=request.text,
            num_points=request.num_points,
            focus=request.focus,
        )
        
        return SummarizeResponse(**result)
    
    except RuntimeError as e:
        logger.error(f"❌ Erreur Ollama : {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama non disponible : {str(e)}",
        ) from e
    
    except Exception as e:
        logger.exception(f"❌ Erreur résumé : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur résumé : {str(e)}",
        ) from e