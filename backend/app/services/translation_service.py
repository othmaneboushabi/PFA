"""Service de traduction multilingue basé sur NLLB-200.

Ce module encapsule la logique de traduction :
    - Support multilingue : FR ↔ EN ↔ ES ↔ AR
    - Chargement paresseux du modèle NLLB-200-distilled-600M
    - Cache Redis pour éviter les re-traductions
    - Gestion des codes langues NLLB spécifiques

Pattern Singleton : une seule instance du modèle NLLB est chargée
en mémoire pour toute l'application.

Codes langues NLLB (pas ISO standard) :
    - Français : fra_Latn
    - Anglais : eng_Latn
    - Espagnol : spa_Latn
    - Arabe MSA : arb_Arab
"""
import hashlib
from typing import Optional

import redis
from loguru import logger

from app.core.config import settings


class TranslationService:
    """Service de traduction via NLLB-200 avec cache Redis.

    Le modèle est chargé de manière paresseuse (lazy loading)
    lors du premier appel à translate().
    """

    # Mapping codes langues ISO → codes langues NLLB
    LANG_CODE_MAPPING = {
        "fr": "fra_Latn",
        "en": "eng_Latn",
        "es": "spa_Latn",
        "ar": "arb_Arab",
    }

    def __init__(self) -> None:
        """Initialise le service de traduction sans charger le modèle."""
        self._model = None
        self._tokenizer = None
        self._redis_client = None
        logger.info("TranslationService initialisé (modèle chargé à la demande)")

    def _get_redis_client(self):
        """Connexion au cache Redis (lazy loading)."""
        if self._redis_client is not None:
            return self._redis_client

        try:
            self._redis_client = redis.Redis(
                host="localhost",
                port=6379,
                db=0,
                decode_responses=True,  # Retourne des strings, pas des bytes
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            # Test de connexion
            self._redis_client.ping()
            logger.success("✅ Connexion Redis établie")
        except redis.ConnectionError:
            logger.warning(
                "⚠️  Redis non accessible, cache désactivé "
                "(traductions non mises en cache)"
            )
            self._redis_client = None

        return self._redis_client

    def _load_model(self):
        """Charge le modèle NLLB-200 (appelé une seule fois)."""
        if self._model is not None:
            return self._model, self._tokenizer

        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        except ImportError:
            logger.error(
                "transformers ou torch n'est pas installé. "
                "Lancez : pip install transformers torch"
            )
            raise

        logger.info("⏳ Chargement du modèle NLLB-200-distilled-600M...")
        model_name = "facebook/nllb-200-distilled-600M"

        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        logger.success(
            "✅ Modèle NLLB chargé (2.4 GB en RAM, "
            "chargement initial ~10-15s)"
        )

        return self._model, self._tokenizer

    def _generate_cache_key(
        self, text: str, src_lang: str, tgt_lang: str
    ) -> str:
        """Génère une clé Redis unique pour une traduction.

        Format : "translation:{src}:{tgt}:{hash}"
        où hash = MD5 du texte (pour éviter les clés trop longues).

        Args:
            text: Texte source
            src_lang: Code langue source (fr, en, es, ar)
            tgt_lang: Code langue cible (fr, en, es, ar)

        Returns:
            Clé Redis (ex: "translation:fr:en:a3b5c7...")
        """
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
        return f"translation:{src_lang}:{tgt_lang}:{text_hash}"

    def translate(
        self,
        text: str,
        src_lang: str = "fr",
        tgt_lang: str = "en",
        use_cache: bool = True,
    ) -> dict:
        """Traduit un texte d'une langue vers une autre.

        Args:
            text: Texte à traduire
            src_lang: Code langue source (fr, en, es, ar)
            tgt_lang: Code langue cible (fr, en, es, ar)
            use_cache: Utiliser le cache Redis (défaut: True)

        Returns:
            dict avec :
                - translated_text (str) : texte traduit
                - src_lang (str) : langue source
                - tgt_lang (str) : langue cible
                - from_cache (bool) : True si résultat vient du cache
                - cache_key (str) : clé Redis utilisée

        Raises:
            ValueError: si langue source ou cible non supportée
        """
        # Validation langues
        if src_lang not in self.LANG_CODE_MAPPING:
            raise ValueError(
                f"Langue source '{src_lang}' non supportée. "
                f"Langues disponibles : {list(self.LANG_CODE_MAPPING.keys())}"
            )
        if tgt_lang not in self.LANG_CODE_MAPPING:
            raise ValueError(
                f"Langue cible '{tgt_lang}' non supportée. "
                f"Langues disponibles : {list(self.LANG_CODE_MAPPING.keys())}"
            )

        # Cas trivial : même langue source et cible
        if src_lang == tgt_lang:
            return {
                "translated_text": text,
                "src_lang": src_lang,
                "tgt_lang": tgt_lang,
                "from_cache": False,
                "cache_key": None,
            }

        cache_key = self._generate_cache_key(text, src_lang, tgt_lang)

        # Tentative de récupération depuis Redis
        if use_cache:
            redis_client = self._get_redis_client()
            if redis_client is not None:
                try:
                    cached = redis_client.get(cache_key)
                    if cached:
                        logger.info(
                            f"✅ Traduction depuis cache : {src_lang}→{tgt_lang}"
                        )
                        return {
                            "translated_text": cached,
                            "src_lang": src_lang,
                            "tgt_lang": tgt_lang,
                            "from_cache": True,
                            "cache_key": cache_key,
                        }
                except redis.RedisError as e:
                    logger.warning(f"⚠️  Erreur Redis (lecture) : {e}")

        # Cache miss → traduction via NLLB
        logger.info(
            f"🌍 Traduction NLLB : {src_lang}→{tgt_lang} | "
            f"texte={len(text)} caractères"
        )

        model, tokenizer = self._load_model()

        # Conversion codes langues ISO → NLLB
        src_lang_nllb = self.LANG_CODE_MAPPING[src_lang]
        tgt_lang_nllb = self.LANG_CODE_MAPPING[tgt_lang]

        # Tokenization
        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

        # Génération traduction
        translated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.lang_code_to_id[tgt_lang_nllb],
            max_length=512,
        )

        # Décodage
        translated_text = tokenizer.decode(
            translated_tokens[0], skip_special_tokens=True
        )

        logger.success(
            f"✅ Traduction NLLB OK : {src_lang}→{tgt_lang} | "
            f"sortie={len(translated_text)} caractères"
        )

        # Sauvegarde dans Redis
        if use_cache:
            redis_client = self._get_redis_client()
            if redis_client is not None:
                try:
                    # TTL de 7 jours (604800 secondes)
                    redis_client.setex(cache_key, 604800, translated_text)
                    logger.debug(f"💾 Sauvegarde cache : {cache_key}")
                except redis.RedisError as e:
                    logger.warning(f"⚠️  Erreur Redis (écriture) : {e}")

        return {
            "translated_text": translated_text,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "from_cache": False,
            "cache_key": cache_key,
        }


# ===== Pattern Singleton =====
_translation_service: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """Retourne l'instance unique du service de traduction (Singleton).

    Garantit qu'un seul modèle NLLB est chargé en mémoire,
    partagé entre toutes les requêtes de l'application.
    """
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service