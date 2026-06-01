"""Routes pour le pipeline orchestré."""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from loguru import logger
import tempfile
from pathlib import Path

from app.schemas.orchestrator import ProcessAudioRequest, ProcessAudioResponse
from app.services.orchestrator_service import get_orchestrator_service

router = APIRouter()


@router.post(
    "/process",
    response_model=ProcessAudioResponse,
    summary="Pipeline complet : Audio → Transcription + NER + Traduction",
    description=(
        "Traite un fichier audio de bout en bout : "
        "transcription, extraction d'entités, traduction, enrichissement glossaire."
    ),
    status_code=status.HTTP_200_OK,
)
async def process_audio(
    file: UploadFile = File(..., description="Fichier audio (WAV, MP3, M4A)"),
    source_lang: str = Form(default="fr", description="Langue source"),
    target_lang: str = Form(default="en", description="Langue cible"),
    extract_entities: bool = Form(default=True, description="Activer NER"),
    translate: bool = Form(default=True, description="Activer traduction"),
    enrich_glossary: bool = Form(default=True, description="Enrichir avec glossaires"),
) -> ProcessAudioResponse:
    """Process un audio complet via le pipeline orchestré."""
    
    logger.info(f"📥 Requête pipeline : {file.filename} | {source_lang}→{target_lang}")
    
    try:
        # Sauvegarder temporairement l'audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Orchestration
        orchestrator = get_orchestrator_service()
        result = await orchestrator.process_audio(
            audio_path=tmp_path,
            source_lang=source_lang,
            target_lang=target_lang,
            extract_entities=extract_entities,
            translate=translate,
            enrich_glossary=enrich_glossary,
        )
        
        # Nettoyer fichier temporaire
        Path(tmp_path).unlink()
        
        return ProcessAudioResponse(**result)
    
    except Exception as e:
        logger.exception(f"❌ Erreur pipeline orchestré : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur pipeline : {str(e)}",
        ) from e