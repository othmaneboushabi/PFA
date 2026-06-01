"""Service de transcription en streaming temps réel via faster-whisper."""
import os
import tempfile
from typing import Optional
from loguru import logger

from app.services.asr_service import get_asr_service


class StreamingService:
    """Service de transcription audio en streaming.
    
    Convertit les chunks WebM/OGG (navigateur) → WAV 16kHz → Whisper.
    """

    def __init__(self):
        self.asr_service = get_asr_service()
        logger.info("StreamingService initialisé (WebM→WAV→Whisper)")

    async def transcribe_stream(
        self,
        audio_chunks: list,
        language: str = "fr",
    ) -> dict:
        """Transcrit un chunk audio WebM → WAV → Whisper."""
        try:
            audio_data = b"".join(audio_chunks)

            if len(audio_data) < 500:
                return {"text": "", "is_final": False}

            logger.info(f"🔄 Conversion audio : {len(audio_data)} bytes")

            # Sauvegarder en fichier temporaire
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
                tmp.write(audio_data)
                webm_path = tmp.name

            wav_path = webm_path.replace(".webm", ".wav")

            # Essayer plusieurs formats
            try:
                from pydub import AudioSegment
                converted = False

                for fmt in ["webm", "ogg", "opus", "mp4"]:
                    try:
                        audio = AudioSegment.from_file(webm_path, format=fmt)
                        audio = audio.set_frame_rate(16000).set_channels(1)
                        audio.export(wav_path, format="wav")
                        converted = True
                        logger.info(f"✅ Conversion OK ({fmt}) : {len(audio)}ms")
                        break
                    except Exception:
                        continue

                os.unlink(webm_path)

                if not converted:
                    logger.error("❌ Tous les formats ont échoué")
                    return {"text": "", "is_final": False}

            except Exception as e:
                logger.error(f"❌ Conversion échouée : {e}")
                if os.path.exists(webm_path):
                    os.unlink(webm_path)
                return {"text": "", "is_final": False}

            # Transcrire avec Whisper
            result = self.asr_service.transcribe(
                audio_path=wav_path,
                language=language,
            )

            if os.path.exists(wav_path):
                os.unlink(wav_path)

            text = result.get("text", "").strip()
            logger.info(f"📝 Texte : '{text[:100]}'" if text else "📝 Texte vide (silence ?)")

            return {
                "text": text,
                "language": result.get("language", language),
                "is_final": True,
            }

        except Exception as e:
            logger.error(f"❌ Erreur streaming : {e}")
            return {"text": "", "is_final": False}


# Singleton
_streaming_service: Optional[StreamingService] = None


def get_streaming_service() -> StreamingService:
    global _streaming_service
    if _streaming_service is None:
        _streaming_service = StreamingService()
    return _streaming_service