"""Service d'orchestration du pipeline complet AIS.

Pipeline :
    Audio → ASR → NER + Translation (parallel) → Enrichissement → Résultat
"""
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

from loguru import logger

from app.services.asr_service import get_asr_service
from app.services.ner_service import get_ner_service
from app.services.translation_service import get_translation_service
from app.services.glossary_service import get_glossary_service


class OrchestratorService:
    """Service d'orchestration des pipelines AIS."""
    
    def __init__(self):
        """Initialise l'orchestrateur."""
        self.asr_service = get_asr_service()
        self.ner_service = get_ner_service()
        self.translation_service = get_translation_service()
        self.glossary_service = get_glossary_service()
        
        logger.info("OrchestratorService initialisé")
    
    async def process_audio(
        self,
        audio_path: str,
        source_lang: str = "fr",
        target_lang: str = "en",
        extract_entities: bool = True,
        translate: bool = True,
        enrich_glossary: bool = True,
    ) -> Dict[str, Any]:
        """Pipeline complet : Audio → Transcription → NER + Translation.
        
        Args:
            audio_path: Chemin vers le fichier audio
            source_lang: Langue source (fr, en, es, ar)
            target_lang: Langue cible pour traduction
            extract_entities: Activer extraction NER
            translate: Activer traduction
            enrich_glossary: Enrichir avec glossaires
            
        Returns:
            Dict avec transcription, entités, traduction, etc.
        """
        logger.info(f"🚀 Début pipeline orchestré : {Path(audio_path).name}")
        
        result = {
            "audio_file": Path(audio_path).name,
            "source_lang": source_lang,
            "target_lang": target_lang,
        }
        
        # ===== Étape 1 : ASR (Transcription) =====
        logger.info("📝 [1/3] Transcription audio...")
        
        transcription_result = self.asr_service.transcribe(
            audio_path=audio_path,
            language=source_lang,
        )
        
        transcription_text = transcription_result["text"]
        result["transcription"] = {
            "text": transcription_text,
            "language": transcription_result["language"],
            "duration": transcription_result.get("duration"),
        }
        
        logger.success(f"✅ Transcription : {len(transcription_text)} caractères")
        
        # ===== Étape 2 : NER + Translation (parallèle) =====
        tasks = []
        
        if extract_entities:
            logger.info("🏷️  [2/3] Extraction entités (NER)...")
            tasks.append(self._extract_entities(transcription_text, source_lang))
        
        if translate:
            logger.info("🌍 [3/3] Traduction...")
            tasks.append(self._translate_text(transcription_text, source_lang, target_lang))
        
        # Exécution parallèle
        if tasks:
            results_parallel = await asyncio.gather(*tasks)
            
            if extract_entities:
                result["entities"] = results_parallel[0]
                logger.success(f"✅ NER : {len(result['entities'])} entités")
            
            if translate:
                translation_idx = 1 if extract_entities else 0
                result["translation"] = results_parallel[translation_idx]
                logger.success(f"✅ Traduction : {len(result['translation']['translated_text'])} caractères")
        
        # ===== Étape 3 : Enrichissement glossaire (optionnel) =====
        # ===== Étape 3 : Enrichissement glossaire (optionnel) =====
        # Désactivé pour l'arabe (pas de glossaires AR disponibles)
        if enrich_glossary and translate and "translation" in result and source_lang != "ar":
            logger.info("📚 Enrichissement avec glossaires...")
            result["glossary_matches"] = await self._enrich_with_glossary(
                transcription_text,
                source_lang,
                target_lang,
            )
            logger.success(f"✅ Glossaire : {len(result['glossary_matches'])} termes trouvés")
        
        logger.success("🎉 Pipeline terminé avec succès")
        
        return result
    
    async def _extract_entities(self, text: str, language: str) -> list:
        """Extraction NER asynchrone."""
        return self.ner_service.extract_entities(text=text, language=language)
    
    async def _translate_text(
        self,
        text: str,
        src_lang: str,
        tgt_lang: str,
    ) -> dict:
        """Traduction asynchrone."""
        return self.translation_service.translate(
            text=text,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
        )
    
    async def _enrich_with_glossary(
        self,
        text: str,
        src_lang: str,
        tgt_lang: str,
    ) -> list:
        """Enrichissement avec glossaires.
        
        Détecte les termes du texte présents dans les glossaires.
        """
        # Extraction mots uniques (simple)
        words = set(text.split())
        
        matches = []
        for word in words:
            # Recherche dans glossaires avec seuil élevé
            results = await self.glossary_service.search_term(
                term=word,
                source_lang=src_lang,
                target_lang=tgt_lang,
                fuzzy_threshold=90,
            )
            
            if results:
                # Prendre le meilleur match
                best_match = results[0]
                matches.append({
                    "term": word,
                    "translation": best_match["target_term"],
                    "context": best_match.get("context"),
                    "domain": best_match.get("domain"),
                    "score": best_match["match_score"],
                })
        
        return matches


# Singleton
_orchestrator_service: Optional[OrchestratorService] = None


def get_orchestrator_service() -> OrchestratorService:
    """Retourne l'instance unique de l'orchestrateur."""
    global _orchestrator_service
    if _orchestrator_service is None:
        _orchestrator_service = OrchestratorService()
    return _orchestrator_service