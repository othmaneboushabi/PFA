"""Service de résumé automatique via Qwen 2.5 7B (Ollama)."""
import time
import requests
from typing import Optional, Dict, Any
from loguru import logger


class SummarizationService:
    """Service de résumé automatique via Qwen 2.5 7B."""

    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "qwen2.5:7b"
    MIN_WORDS_FOR_SUMMARY = 100

    def __init__(self):
        logger.info(f"SummarizationService initialisé ({self.MODEL_NAME})")

    def _call_ollama(self, prompt: str, timeout: int = 120) -> str:
        """Appelle Ollama pour générer du texte."""
        try:
            payload = {
                "model": self.MODEL_NAME,
                "prompt": prompt,          # ← prompt (pas messages !)
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_gpu": 99,         # ← Forcer GPU
                }
            }

            response = requests.post(
                self.OLLAMA_API_URL,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()

            result = response.json()
            generated_text = result.get("response", "").strip()

            # Retry si réponse vide
            retries = 0
            while not generated_text and retries < 3:
                retries += 1
                logger.warning(f"⚠️  Réponse vide, retry {retries}/3...")
                time.sleep(5)
                response = requests.post(
                    self.OLLAMA_API_URL,
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                result = response.json()
                generated_text = result.get("response", "").strip()

            logger.debug(f"📥 Réponse Ollama : {len(generated_text)} chars")
            return generated_text

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur Ollama : {e}")
            raise RuntimeError(f"Ollama API error: {e}") from e

    def should_summarize(self, text: str) -> bool:
        word_count = len(text.split())
        return word_count >= self.MIN_WORDS_FOR_SUMMARY

    def summarize(
        self,
        text: str,
        num_points: int = 5,
        focus: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Génère un résumé du texte en bullet points."""
        word_count = len(text.split())

        logger.info(f"📝 Résumé : {word_count} mots → {num_points} points")

        if not self.should_summarize(text):
            logger.warning(f"⚠️  Texte trop court ({word_count} mots)")
            return {
                "summary": text,
                "word_count": word_count,
                "num_points": 0,
                "summarized": False,
            }

        focus_instruction = f"\nFocus on: {focus}" if focus else ""

        prompt = f"""Summarize the following text in {num_points} concise bullet points.
Each bullet point should be a complete sentence.
Do NOT include any preamble or conclusion, ONLY the bullet points.{focus_instruction}

Text to summarize:
{text}

Summary (bullet points only):
"""

        summary_text = self._call_ollama(prompt)

        # Parser les bullet points
        lines = [line.strip() for line in summary_text.split('\n') if line.strip()]

        bullet_points = []
        for line in lines:
            clean_line = line.lstrip('-*•0123456789. ')
            if clean_line and len(clean_line) > 20:
                bullet_points.append(clean_line)

        logger.success(f"✅ Résumé généré : {len(bullet_points)} points")

        return {
            "summary": bullet_points,
            "word_count": word_count,
            "num_points": len(bullet_points),
            "summarized": True,
            "original_length": len(text),
            "compression_ratio": round(len(' '.join(bullet_points)) / len(text), 2),
        }


_summarization_service: Optional[SummarizationService] = None


def get_summarization_service() -> SummarizationService:
    global _summarization_service
    if _summarization_service is None:
        _summarization_service = SummarizationService()
    return _summarization_service