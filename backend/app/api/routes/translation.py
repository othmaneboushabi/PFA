"""Routes de traduction multilingue.

Endpoints :
    POST /translate : traduction d'un texte d'une langue vers une autre

Cet endpoint utilise NLLB-200 avec cache Redis pour éviter
les re-traductions des mêmes phrases.
"""
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.schemas.translation import TranslationRequest, TranslationResponse
from app.services.translation_service import get_translation_service

router = APIRouter()


@router.post(
    "/translate",
    response_model=TranslationResponse,
    summary="Traduction multilingue",
    description=(
        "Traduit un texte d'une langue vers une autre via NLLB-200. "
        "Langues supportées : FR, EN, ES, AR. "
        "Cache Redis activé par défaut pour accélérer les traductions répétées."
    ),
    status_code=status.HTTP_200_OK,
)
async def translate_text(request: TranslationRequest) -> TranslationResponse:
    """Traduit un texte donné."""

    logger.info(
        f"📥 Requête traduction reçue : {request.src_lang}→{request.tgt_lang}, "
        f"texte={len(request.text)} caractères"
    )

    try:
        # Validation : même langue source et cible
        if request.src_lang == request.tgt_lang:
            logger.warning(
                f"⚠️  Langue source = langue cible ({request.src_lang}), "
                "retour du texte original"
            )
            return TranslationResponse(
                original_text=request.text,
                translated_text=request.text,
                src_lang=request.src_lang,
                tgt_lang=request.tgt_lang,
                from_cache=False,
                char_count=len(request.text),
            )

        # Traduction via service
        translation_service = get_translation_service()
        result = translation_service.translate(
            text=request.text,
            src_lang=request.src_lang,
            tgt_lang=request.tgt_lang,
            use_cache=request.use_cache,
        )

        # Construction de la réponse
        return TranslationResponse(
            original_text=request.text,
            translated_text=result["translated_text"],
            src_lang=result["src_lang"],
            tgt_lang=result["tgt_lang"],
            from_cache=result["from_cache"],
            char_count=len(result["translated_text"]),
        )

    except ValueError as e:
        logger.error(f"❌ Erreur de validation : {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except Exception as e:
        logger.exception(f"❌ Erreur lors de la traduction : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la traduction : {str(e)}",
        ) from e