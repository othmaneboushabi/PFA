"""Routes de traduction via Gemma 2 9B (Ollama)."""
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.schemas.translation import TranslationRequest, TranslationResponse
from app.services.translation_service import get_translation_service

router = APIRouter()


@router.post(
    "/translate",
    response_model=TranslationResponse,
    summary="Traduction multilingue (Gemma 2 9B)",
    description=(
        "Traduit un texte via Gemma 2 9B (Ollama). "
        "Langues supportées : FR, EN, ES, AR. "
        "Utilise le GPU RTX 4060 pour performances optimales."
    ),
    status_code=status.HTTP_200_OK,
)
async def translate_text_gemma(request: TranslationRequest) -> TranslationResponse:
    """Traduit un texte via Gemma 2 9B."""
    
    logger.info(
        f"📥 Requête traduction Gemma : {request.src_lang}→{request.tgt_lang}"
    )

    try:
        if request.src_lang == request.tgt_lang:
            return TranslationResponse(
                original_text=request.text,
                translated_text=request.text,
                src_lang=request.src_lang,
                tgt_lang=request.tgt_lang,
                from_cache=False,
                char_count=len(request.text),
            )

        translation_service = get_translation_service()
        result = translation_service.translate(
            text=request.text,
            src_lang=request.src_lang,
            tgt_lang=request.tgt_lang,
            use_cache=request.use_cache,
        )

        return TranslationResponse(
            original_text=request.text,
            translated_text=result["translated_text"],
            src_lang=result["src_lang"],
            tgt_lang=result["tgt_lang"],
            from_cache=result["from_cache"],
            char_count=len(result["translated_text"]),
        )

    except ValueError as e:
        logger.error(f"❌ Erreur validation : {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except RuntimeError as e:
        logger.error(f"❌ Erreur Ollama : {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama non disponible : {str(e)}",
        ) from e

    except Exception as e:
        logger.exception(f"❌ Erreur traduction Gemma : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur traduction : {str(e)}",
        ) from e