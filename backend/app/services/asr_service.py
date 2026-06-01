"""Service ASR (Automatic Speech Recognition) basé sur faster-whisper.

Ce module encapsule la logique de transcription audio :
    - Chargement paresseux du modèle Whisper
    - Transcription d'un fichier audio (WAV, MP3, FLAC, etc.)
    - Détection automatique de la langue
    - Mesure de la latence end-to-end

Pattern Singleton : une seule instance de WhisperModel est chargée
en mémoire pour toute l'application.

TODO J6 :
    - Intégrer whisper-streaming pour le streaming temps réel
    - Ajouter VAD (Voice Activity Detection)
    - Exposer via WebSocket pour l'UI
"""
import os
import sys

# Ajouter les DLLs CUDA 12 au PATH pour faster-whisper
_cuda_paths = [
    os.path.join(sys.prefix, "Lib", "site-packages", "nvidia", "cublas", "bin"),
    os.path.join(sys.prefix, "Lib", "site-packages", "nvidia", "cudnn", "bin"),
    os.path.join(sys.prefix, "Lib", "site-packages", "nvidia", "cuda_nvrtc", "bin"),
]
for _path in _cuda_paths:
    if os.path.exists(_path):
        os.add_dll_directory(_path)
        
import time
from typing import Optional

from loguru import logger

from app.core.config import settings



class ASRService:
    """Service de transcription audio via faster-whisper.

    Le modèle est chargé de manière paresseuse (lazy loading)
    lors du premier appel à transcribe(), pour ne pas ralentir
    le démarrage de l'application.
    """

    def __init__(self) -> None:
        self._model = None
        self.model_name: str = settings.whisper_model
        self.device: str = settings.whisper_device
        self.compute_type: str = settings.whisper_compute_type
        logger.info(
            f"ASRService initialisé (modèle={self.model_name}, "
            f"device={self.device}, compute={self.compute_type})"
        )

    def _load_model(self):
        """Charge le modèle Whisper en mémoire (appelé une seule fois)."""
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel
        except ImportError:
            logger.error(
                "faster-whisper n'est pas installé. "
                "Lancez : pip install faster-whisper"
            )
            raise

        logger.info(
            f"⏳ Chargement du modèle Whisper '{self.model_name}'... "
            "(1ère fois : téléchargement ~460 MB si pas en cache)"
        )
        start = time.time()

        self._model = WhisperModel(
            self.model_name,
            device=self.device,
            compute_type=self.compute_type,
        )

        elapsed = time.time() - start
        logger.success(f"✅ Modèle Whisper chargé en {elapsed:.2f}s")
        return self._model

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        beam_size: int = 5,
    ) -> dict:
        """Transcrit un fichier audio.

        Args:
            audio_path: Chemin vers le fichier audio (WAV, MP3, M4A, FLAC).
            language: Code langue ('fr', 'en', 'es', 'ar').
                Si None ou 'auto', détection automatique.
            beam_size: Taille du beam search (5 = défaut, qualité/vitesse).

        Returns:
            dict avec :
                - text (str) : transcription complète
                - language (str) : code langue détecté
                - language_probability (float) : confiance détection langue
                - duration (float) : durée audio en secondes
                - segments (list) : liste des segments {start, end, text}
                - latency_ms (float) : latence de transcription en ms
                - realtime_factor (float) : ratio durée_audio / latence
        """
        model = self._load_model()

        # Normalisation de la langue
        lang = None if language in (None, "", "auto") else language

        logger.info(f"🎤 Transcription : {audio_path} (langue={lang or 'auto'})")
        start = time.time()

        segments, info = model.transcribe(
            audio_path,
            language=lang,
            beam_size=beam_size,
            vad_filter=True,  # Filtre les silences
        )

        # Matérialise le générateur pour construire la transcription complète
        segments_list: list[dict] = []
        full_text_parts: list[str] = []

        for seg in segments:
            segments_list.append(
                {
                    "start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip(),
                }
            )
            full_text_parts.append(seg.text)

        latency_ms = (time.time() - start) * 1000
        full_text = "".join(full_text_parts).strip()

        # Facteur temps réel : si > 1, transcription plus rapide que l'audio
        realtime_factor = (
            (info.duration * 1000) / latency_ms if latency_ms > 0 else 0
        )

        logger.success(
            f"✅ Transcription OK | langue={info.language} "
            f"(conf={info.language_probability:.0%}) | "
            f"durée={info.duration:.1f}s | "
            f"latence={latency_ms:.0f}ms | "
            f"RTF={realtime_factor:.2f}x"
        )

        return {
            "text": full_text,
            "language": info.language,
            "language_probability": round(info.language_probability, 4),
            "duration": round(info.duration, 2),
            "segments": segments_list,
            "latency_ms": round(latency_ms, 2),
            "realtime_factor": round(realtime_factor, 2),
        }


# ===== Pattern Singleton =====
_asr_service: Optional[ASRService] = None


def get_asr_service() -> ASRService:
    """Retourne l'instance unique du service ASR (Singleton).

    Garantit qu'un seul modèle Whisper est chargé en mémoire,
    partagé entre toutes les requêtes de l'application.
    """
    global _asr_service
    if _asr_service is None:
        _asr_service = ASRService()
    return _asr_service