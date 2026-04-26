"""Service NER (Named Entity Recognition) multilingue basé sur spaCy.

Ce module encapsule la logique d'extraction d'entités nommées :
    - Support multilingue : FR, EN, ES (AR via CAMeL-BERT en J11-J12)
    - Chargement paresseux des modèles spaCy
    - Normalisation des labels pour uniformiser l'API
    - Détection automatique ou manuelle de la langue

Pattern Singleton : une seule instance de chaque modèle spaCy est chargée
en mémoire pour toute l'application.

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
    """Service d'extraction d'entités nommées via spaCy.

    Les modèles sont chargés de manière paresseuse (lazy loading)
    lors du premier appel à extract_entities(), pour ne pas ralentir
    le démarrage de l'application.
    """

    # Mapping de normalisation des labels spaCy vers labels AIS uniformes
    LABEL_MAPPING = {
        # Labels français (fr_core_news_lg)
        "PER": "PER",
        "LOC": "LOC",
        "ORG": "ORG",
        "MISC": "MISC",
        # Labels anglais (en_core_web_lg)
        "PERSON": "PER",
        "GPE": "LOC",  # GeoPolitical Entity → Lieu
        "FAC": "LOC",  # Facility → Lieu
        "NORP": "MISC",  # Nationalités, groupes religieux/politiques
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
        # Labels espagnol (es_core_news_lg) — similaire au français
        # Pas besoin de répéter PER/LOC/ORG/MISC déjà mappés
    }

    def __init__(self) -> None:
        """Initialise le service NER sans charger les modèles."""
        self._nlp_fr = None
        self._nlp_en = None
        self._nlp_es = None
        logger.info("NERService initialisé (modèles chargés à la demande)")

    def _load_model_fr(self):
        """Charge le modèle français (appelé une seule fois)."""
        if self._nlp_fr is not None:
            return self._nlp_fr

        try:
            import spacy
        except ImportError:
            logger.error(
                "spaCy n'est pas installé. Lancez : pip install spacy==3.7.4"
            )
            raise

        logger.info("⏳ Chargement du modèle NER français...")
        self._nlp_fr = spacy.load("fr_core_news_lg")
        logger.success("✅ Modèle français chargé")
        return self._nlp_fr

    def _load_model_en(self):
        """Charge le modèle anglais (appelé une seule fois)."""
        if self._nlp_en is not None:
            return self._nlp_en

        try:
            import spacy
        except ImportError:
            logger.error(
                "spaCy n'est pas installé. Lancez : pip install spacy==3.7.4"
            )
            raise

        logger.info("⏳ Chargement du modèle NER anglais...")
        self._nlp_en = spacy.load("en_core_web_lg")
        logger.success("✅ Modèle anglais chargé")
        return self._nlp_en

    def _load_model_es(self):
        """Charge le modèle espagnol (appelé une seule fois)."""
        if self._nlp_es is not None:
            return self._nlp_es

        try:
            import spacy
        except ImportError:
            logger.error(
                "spaCy n'est pas installé. Lancez : pip install spacy==3.7.4"
            )
            raise

        logger.info("⏳ Chargement du modèle NER espagnol...")
        self._nlp_es = spacy.load("es_core_news_lg")
        logger.success("✅ Modèle espagnol chargé")
        return self._nlp_es

    def _normalize_label(self, label: str) -> str:
        """Normalise un label spaCy vers un label AIS standard.

        Args:
            label: Label brut retourné par spaCy (ex: "PERSON", "GPE", "MONEY")

        Returns:
            Label normalisé AIS (ex: "PER", "LOC", "NUM")
        """
        return self.LABEL_MAPPING.get(label, "MISC")

    def extract_entities(
        self,
        text: str,
        language: str = "fr",
    ) -> list[dict]:
        """Extrait les entités nommées d'un texte.

        Args:
            text: Texte à analyser (transcription audio).
            language: Code langue ('fr', 'en', 'es').

        Returns:
            Liste de dictionnaires avec :
                - text (str) : texte de l'entité
                - label (str) : catégorie normalisée (PER, ORG, LOC, DATE, NUM, MISC)
                - start (int) : position de début (caractères)
                - end (int) : position de fin (caractères)

        Raises:
            ValueError: si la langue n'est pas supportée.
        """
        # Sélection du modèle selon la langue
        if language == "fr":
            nlp = self._load_model_fr()
        elif language == "en":
            nlp = self._load_model_en()
        elif language == "es":
            nlp = self._load_model_es()
        else:
            raise ValueError(
                f"Langue '{language}' non supportée. "
                "Langues disponibles : fr, en, es"
            )

        logger.info(f"🔍 Extraction NER : langue={language}, texte={len(text)} caractères")

        # Traitement NER
        doc = nlp(text)

        # Construction de la liste d'entités normalisées
        entities = []
        for ent in doc.ents:
            normalized_label = self._normalize_label(ent.label_)
            entities.append(
                {
                    "text": ent.text,
                    "label": normalized_label,
                    "start": ent.start_char,
                    "end": ent.end_char,
                }
            )

        logger.success(
            f"✅ NER OK : {len(entities)} entités détectées "
            f"({', '.join(set(e['label'] for e in entities))})"
        )

        return entities


# ===== Pattern Singleton =====
_ner_service: Optional[NERService] = None


def get_ner_service() -> NERService:
    """Retourne l'instance unique du service NER (Singleton).

    Garantit qu'un seul ensemble de modèles spaCy est chargé en mémoire,
    partagé entre toutes les requêtes de l'application.
    """
    global _ner_service
    if _ner_service is None:
        _ner_service = NERService()
    return _ner_service