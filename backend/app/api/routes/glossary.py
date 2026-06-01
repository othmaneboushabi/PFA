"""Routes API pour la gestion des glossaires terminologiques."""
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from loguru import logger

from app.schemas.glossary import (
    GlossaryUploadResponse,
    GlossarySearchRequest,
    GlossarySearchResponse,
    GlossaryEntryResult,
)
from app.services.glossary_service import get_glossary_service

router = APIRouter()


@router.post(
    "/glossary/upload",
    response_model=GlossaryUploadResponse,
    summary="Upload d'un glossaire terminologique",
    description=(
        "Importe un glossaire au format CSV, JSON, XLSX ou TBX. "
        "Le glossaire sera utilisé pour améliorer les traductions de termes spécialisés."
    ),
    status_code=status.HTTP_201_CREATED,
)
async def upload_glossary(
    file: UploadFile = File(..., description="Fichier glossaire"),
    format_type: str = Form(..., description="Format : csv, json, xlsx, ou tbx"),
) -> GlossaryUploadResponse:
    """Upload et parse un fichier glossaire."""
    
    logger.info(
        f"📥 Upload glossaire : {file.filename} | format={format_type}"
    )
    
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        # Valider la taille (max 10 MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Fichier trop volumineux (max 10 MB)",
            )
        
        # Upload via service
        glossary_service = get_glossary_service()
        result = await glossary_service.upload_glossary(
            file_content=content,
            filename=file.filename,
            format_type=format_type.lower(),
        )
        
        return GlossaryUploadResponse(**result)
    
    except ValueError as e:
        logger.error(f"❌ Erreur validation : {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    
    except NotImplementedError as e:
        logger.error(f"❌ Format non implémenté : {e}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e),
        ) from e
    
    except Exception as e:
        logger.exception(f"❌ Erreur upload glossaire : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload : {str(e)}",
        ) from e


@router.post(
    "/glossary/search",
    response_model=GlossarySearchResponse,
    summary="Recherche un terme dans les glossaires",
    description=(
        "Recherche un terme avec fuzzy matching (tolérance aux fautes). "
        "Retourne les traductions correspondantes avec score de correspondance."
    ),
    status_code=status.HTTP_200_OK,
)
async def search_term(request: GlossarySearchRequest) -> GlossarySearchResponse:
    """Recherche un terme dans les glossaires uploadés."""
    
    logger.info(
        f"🔍 Recherche glossaire : '{request.term}' | "
        f"{request.source_lang}→{request.target_lang}"
    )
    
    try:
        glossary_service = get_glossary_service()
        results = await glossary_service.search_term(
            term=request.term,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            glossary_id=request.glossary_id,
            fuzzy_threshold=request.fuzzy_threshold,
        )
        
        # Conversion en schémas Pydantic
        results_pydantic = [
            GlossaryEntryResult(**result) for result in results
        ]
        
        return GlossarySearchResponse(
            query_term=request.term,
            results_count=len(results_pydantic),
            results=results_pydantic,
        )
    
    except Exception as e:
        logger.exception(f"❌ Erreur recherche glossaire : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la recherche : {str(e)}",
        ) from e