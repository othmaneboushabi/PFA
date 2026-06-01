"""Service NER (Named Entity Recognition) multilingue basé sur spaCy + HuggingFace.

Support multilingue :
    - FR : fr_core_news_lg (spaCy)
    - EN : en_core_web_lg (spaCy)
    - ES : es_core_news_lg (spaCy)
    - AR : CAMeL-Lab/bert-base-arabic-camelbert-msa-ner (HuggingFace)

Labels normalisés retournés :
    - PER : personnes
    - ORG : organisations
    - LOC : lieux géographiques
    - DATE : dates et durées
    - NUM : nombres, montants, pourcentages
    - MISC : entités diverses
"""
from typing import Optional

from loguru import logger


class NERService:
    """Service d'extraction d'entités nommées via spaCy + HuggingFace."""

    LABEL_MAPPING = {
        # Labels français (fr_core_news_lg)
        "PER": "PER",
        "LOC": "LOC",
        "ORG": "ORG",
        "MISC": "MISC",
        # Labels anglais (en_core_web_lg)
        "PERSON": "PER",
        "GPE": "LOC",
        "FAC": "LOC",
        "NORP": "MISC",
        "MONEY": "NUM",
        "CARDINAL": "NUM",
        "PERCENT": "NUM",
        "QUANTITY": "NUM",
        "ORDINAL": "NUM",
        "DATE": "DATE",
        "TIME": "DATE",
        "EVENT": "MISC",
        "WORK_OF_ART": "MISC",
        "LAW": "MISC",
        "LANGUAGE": "MISC",
        "PRODUCT": "MISC",
        # Labels CAMeL BERT (arabe)
        "PERS": "PER",
        "ORG": "ORG",
    }

    # Modèle HuggingFace pour l'arabe
    AR_MODEL = "CAMeL-Lab/bert-base-arabic-camelbert-msa-ner"

    def __init__(self) -> None:
        """Initialise le service NER sans charger les modèles."""
        self._nlp_fr = None
        self._nlp_en = None
        self._nlp_es = None
        self._nlp_ar = None
        logger.info("NERService initialisé (modèles chargés à la demande)")

    # ==================== spaCy Models ====================

    def _load_model_fr(self):
        """Charge le modèle français (lazy loading)."""
        if self._nlp_fr is not None:
            return self._nlp_fr
        try:
            import spacy
        except ImportError:
            logger.error("spaCy n'est pas installé.")
            raise
        logger.info("⏳ Chargement du modèle NER français...")
        self._nlp_fr = spacy.load("fr_core_news_lg")
        logger.success("✅ Modèle français chargé")
        return self._nlp_fr

    def _load_model_en(self):
        """Charge le modèle anglais (lazy loading)."""
        if self._nlp_en is not None:
            return self._nlp_en
        try:
            import spacy
        except ImportError:
            logger.error("spaCy n'est pas installé.")
            raise
        logger.info("⏳ Chargement du modèle NER anglais...")
        self._nlp_en = spacy.load("en_core_web_lg")
        logger.success("✅ Modèle anglais chargé")
        return self._nlp_en

    def _load_model_es(self):
        """Charge le modèle espagnol (lazy loading)."""
        if self._nlp_es is not None:
            return self._nlp_es
        try:
            import spacy
        except ImportError:
            logger.error("spaCy n'est pas installé.")
            raise
        logger.info("⏳ Chargement du modèle NER espagnol...")
        self._nlp_es = spacy.load("es_core_news_lg")
        logger.success("✅ Modèle espagnol chargé")
        return self._nlp_es

    # ==================== HuggingFace Arabic Model ====================

    def _load_model_ar(self):
        """Charge le modèle NER arabe via HuggingFace (lazy loading).
        
        Modèle : CAMeL-Lab/bert-base-arabic-camelbert-msa-ner
        Téléchargement automatique (~500 MB) au premier appel.
        GPU activé automatiquement si disponible.
        """
        if self._nlp_ar is not None:
            return self._nlp_ar
        try:
            import torch
            from transformers import pipeline
            
            device = 0 if torch.cuda.is_available() else -1
            logger.info(f"⏳ Chargement du modèle NER arabe : {self.AR_MODEL}...")
            logger.info(f"   Device : {'GPU CUDA' if device == 0 else 'CPU'}")
            
            self._nlp_ar = pipeline(
                "ner",
                model=self.AR_MODEL,
                aggregation_strategy="simple",
                device=device,
            )
            logger.success(f"✅ Modèle NER arabe chargé ({'GPU' if device == 0 else 'CPU'})")
            return self._nlp_ar
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle arabe : {e}")
            return None

    # ==================== Label Normalization ====================

    def _normalize_label(self, label: str) -> str:
        """Normalise un label vers un label AIS standard."""
        return self.LABEL_MAPPING.get(label, "MISC")

    # ==================== Main Method ====================

    def extract_entities(
        self,
        text: str,
        language: str = "fr",
    ) -> list[dict]:
        """Extrait les entités nommées d'un texte.

        Args:
            text: Texte à analyser.
            language: Code langue ('fr', 'en', 'es', 'ar').

        Returns:
            Liste de dicts avec text, label, start, end.

        Raises:
            ValueError: si la langue n'est pas supportée.
        """
        # ===== Arabe : HuggingFace CAMeL BERT =====
        if language == "ar":
            nlp = self._load_model_ar()
            if nlp is None:
                logger.warning("⚠️  NER arabe non disponible, retour liste vide.")
                return []

            logger.info(f"🔍 Extraction NER arabe : {len(text)} caractères")
            try:
                raw_entities = nlp(text)
                entities = []
                prev = None

                for ent in raw_entities:
                    label = ent.get("entity_group", "MISC")
                    normalized = self._normalize_label(label)
                    word = ent.get("word", "").replace("##", "").strip()
                    start = ent.get("start", 0)
                    end = ent.get("end", 0)

                    if not word:
                        continue

                    # Fusionner entités adjacentes (fix subwords BERT)
                    if prev and prev["label"] == normalized and start <= prev["end"] + 1:
                        prev["text"] = text[prev["start"]:end]
                        prev["end"] = end
                    else:
                        if prev:
                            entities.append(prev)
                        prev = {"text": word, "label": normalized, "start": start, "end": end}

                if prev:
                    entities.append(prev)

                logger.success(
                    f"✅ NER AR OK : {len(entities)} entités "
                    f"({', '.join(set(e['label'] for e in entities)) if entities else 'aucune'})"
                )
                return entities
            except Exception as e:
                logger.error(f"❌ Erreur NER arabe : {e}")
                return []

        # ===== Autres langues : spaCy =====
        if language == "fr":
            nlp = self._load_model_fr()
        elif language == "en":
            nlp = self._load_model_en()
        elif language == "es":
            nlp = self._load_model_es()
        else:
            raise ValueError(
                f"Langue '{language}' non supportée. "
                "Langues disponibles : fr, en, es, ar"
            )

        logger.info(f"🔍 Extraction NER : langue={language}, texte={len(text)} caractères")

        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            normalized_label = self._normalize_label(ent.label_)
            entities.append({
                "text": ent.text,
                "label": normalized_label,
                "start": ent.start_char,
                "end": ent.end_char,
            })

        logger.success(
            f"✅ NER OK : {len(entities)} entités "
            f"({', '.join(set(e['label'] for e in entities)) if entities else 'aucune'})"
        )
        return entities


# ===== Pattern Singleton =====
_ner_service: Optional[NERService] = None


def get_ner_service() -> NERService:
    """Retourne l'instance unique du service NER."""
    global _ner_service
    if _ner_service is None:
        _ner_service = NERService()
    return _ner_service