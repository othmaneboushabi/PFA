"""Service de traduction via Qwen 2.5 7B (Ollama)."""
import hashlib
import time
import requests
from typing import Optional

import redis
from loguru import logger

from app.core.config import settings


class TranslationServiceGemma:
    """Service de traduction via Qwen 2.5 7B avec cache Redis."""

    LANG_NAMES = {
        "fr": "French",
        "en": "English",
        "es": "Spanish",
        "ar": "Arabic",
    }

    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "qwen2.5:7b"

    def __init__(self) -> None:
        self._redis_client = None
        logger.info(f"TranslationService initialisé (Ollama + {self.MODEL_NAME})")
        self._warmup()

    def _warmup(self):
        """Précharge le modèle au démarrage."""
        try:
            logger.info(f"⏳ Préchargement {self.MODEL_NAME}...")
            response = requests.post(
                self.OLLAMA_API_URL,
                json={
                    "model": self.MODEL_NAME,
                    "prompt": "Hello",
                    "stream": False,
                    "options": {"num_gpu": 99}
                },
                timeout=60,
            )
            result = response.json()
            if result.get("done_reason") == "load":
                logger.info("⏳ Modèle en chargement, attente 3s...")
                time.sleep(3)
            logger.success(f"✅ {self.MODEL_NAME} prêt !")
        except Exception as e:
            logger.warning(f"⚠️  Warmup échoué : {e}")

    def _get_redis_client(self):
        if self._redis_client is not None:
            return self._redis_client
        try:
            self._redis_client = redis.Redis(
                host="localhost", port=6379, db=0,
                decode_responses=True,
                socket_connect_timeout=2, socket_timeout=2,
            )
            self._redis_client.ping()
            logger.success("✅ Connexion Redis établie")
        except redis.ConnectionError:
            logger.warning("⚠️  Redis non accessible, cache désactivé")
            self._redis_client = None
        return self._redis_client

    def _generate_cache_key(self, text: str, src_lang: str, tgt_lang: str) -> str:
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
        return f"translation:qwen:{src_lang}:{tgt_lang}:{text_hash}"

    def _split_text(self, text: str, max_chars: int = 300) -> list:
        """Découpe un texte long en chunks."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        for word in words:
            word_length = len(word) + 1
            if current_length + word_length > max_chars and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def _call_ollama(self, prompt: str) -> str:
        """Appelle l'API Ollama avec retry automatique."""
        try:
            payload = {
                "model": self.MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_gpu": 99,
                }
            }
            logger.debug(f"📤 Appel Ollama : {self.MODEL_NAME}")
            response = requests.post(
                self.OLLAMA_API_URL,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
            generated_text = result.get("response", "").strip()

            # Retry si réponse vide
            retries = 0
            while not generated_text and retries < 3:
                retries += 1
                logger.warning(f"⚠️  Réponse vide, attente 5s... (retry {retries}/3)")
                time.sleep(5)
                response = requests.post(
                    self.OLLAMA_API_URL,
                    json=payload,
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()
                generated_text = result.get("response", "").strip()

            logger.debug(f"📥 Réponse reçue ({len(generated_text)} chars)")
            return generated_text

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur Ollama : {e}")
            raise RuntimeError(f"Ollama API error: {e}") from e

    def translate(
        self,
        text: str,
        src_lang: str = "fr",
        tgt_lang: str = "en",
        use_cache: bool = True,
    ) -> dict:
        """Traduit un texte via Qwen 2.5 7B."""
        if src_lang not in self.LANG_NAMES:
            raise ValueError(f"Langue source '{src_lang}' non supportée.")
        if tgt_lang not in self.LANG_NAMES:
            raise ValueError(f"Langue cible '{tgt_lang}' non supportée.")

        if src_lang == tgt_lang:
            return {
                "original_text": text,
                "translated_text": text,
                "src_lang": src_lang,
                "tgt_lang": tgt_lang,
                "from_cache": False,
                "cache_key": None,
                "char_count": len(text),
            }

        cache_key = self._generate_cache_key(text, src_lang, tgt_lang)

        # Cache Redis
        if use_cache:
            redis_client = self._get_redis_client()
            if redis_client is not None:
                try:
                    cached = redis_client.get(cache_key)
                    if cached:
                        logger.info(f"✅ Cache hit : {src_lang}→{tgt_lang}")
                        return {
                            "original_text": text,
                            "translated_text": cached,
                            "src_lang": src_lang,
                            "tgt_lang": tgt_lang,
                            "from_cache": True,
                            "cache_key": cache_key,
                            "char_count": len(text),
                        }
                except redis.RedisError as e:
                    logger.warning(f"⚠️  Erreur Redis (lecture) : {e}")

        logger.info(f"🌍 Traduction {self.MODEL_NAME} : {src_lang}→{tgt_lang} | {len(text)} chars")

        src_lang_name = self.LANG_NAMES[src_lang]
        tgt_lang_name = self.LANG_NAMES[tgt_lang]

        # Chunking pour textes longs
        if len(text) > 300:
            logger.info(f"📄 Texte long ({len(text)} chars) → découpage en chunks")
            chunks = self._split_text(text, max_chars=300)
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                logger.info(f"   Chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
                prompt = (
                    f"You are a professional translator. "
                    f"Translate the following text from {src_lang_name} to {tgt_lang_name}. "
                    f"IMPORTANT: Respond ONLY in {tgt_lang_name}. "
                    f"Do NOT use Chinese or any other language. "
                    f"Output ONLY the translation, nothing else.\n\n"
                    f"Text: {chunk}\n\n"
                    f"{tgt_lang_name} translation:"
                )
                chunk_translation = self._call_ollama(prompt)
                translated_chunks.append(chunk_translation)
            translated_text = " ".join(translated_chunks)
            logger.success(f"✅ {len(chunks)} chunks traduits → {len(translated_text)} chars")
        else:
            prompt = (
                f"You are a professional translator. "
                f"Translate the following text from {src_lang_name} to {tgt_lang_name}. "
                f"IMPORTANT: Respond ONLY in {tgt_lang_name}. "
                f"Do NOT use Chinese or any other language. "
                f"Output ONLY the translation, nothing else.\n\n"
                f"Text: {text}\n\n"
                f"{tgt_lang_name} translation:"
            )
            translated_text = self._call_ollama(prompt)

        logger.success(f"✅ Traduction OK : {src_lang}→{tgt_lang} | {len(translated_text)} chars")

        # Sauvegarde cache
        if use_cache:
            redis_client = self._get_redis_client()
            if redis_client is not None:
                try:
                    redis_client.setex(cache_key, 604800, translated_text)
                    logger.debug(f"💾 Cache sauvegardé : {cache_key}")
                except redis.RedisError as e:
                    logger.warning(f"⚠️  Erreur Redis (écriture) : {e}")

        return {
            "original_text": text,
            "translated_text": translated_text,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "from_cache": False,
            "cache_key": cache_key,
            "char_count": len(text),
        }


_translation_service: Optional[TranslationServiceGemma] = None


def get_translation_service() -> TranslationServiceGemma:
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationServiceGemma()
    return _translation_service