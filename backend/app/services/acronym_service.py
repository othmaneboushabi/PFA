"""Service d'extraction et d'explication d'acronymes via Qwen 2.5 7B."""
import re
import time
import requests
from typing import List, Dict, Any, Optional
from loguru import logger

from app.services.glossary_service import get_glossary_service


class AcronymService:
    """Service d'extraction et d'explication d'acronymes."""

    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "qwen2.5:7b"
    ACRONYM_PATTERN = r'\b[A-Z]{2,}\b'

    def __init__(self):
        self.glossary_service = get_glossary_service()
        logger.info(f"AcronymService initialisé ({self.MODEL_NAME} + Glossaires)")

    def _call_ollama(self, prompt: str, timeout: int = 60) -> str:
        """Appelle Ollama pour générer une explication."""
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

            return generated_text

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur Ollama : {e}")
            raise RuntimeError(f"Ollama API error: {e}") from e

    def extract_acronyms(self, text: str) -> List[str]:
        acronyms = re.findall(self.ACRONYM_PATTERN, text)
        unique_acronyms = sorted(set(acronyms))
        logger.info(f"🔤 {len(unique_acronyms)} acronymes détectés : {unique_acronyms}")
        return unique_acronyms

    async def explain_acronym(
        self,
        acronym: str,
        context: str = "",
        domain: Optional[str] = None,
        source_lang: str = "fr",
        target_lang: str = "en",
    ) -> Dict[str, Any]:
        """Explique un acronyme via glossaire ou Qwen 2.5."""
        logger.info(f"🔍 Explication acronyme : '{acronym}'")

        # Chercher dans glossaires d'abord
        glossary_results = await self.glossary_service.search_term(
            term=acronym,
            source_lang=source_lang,
            target_lang=target_lang,
            fuzzy_threshold=95,
        )

        if glossary_results:
            best_match = glossary_results[0]
            logger.success(f"✅ Trouvé dans glossaire : {acronym} → {best_match['target_term']}")
            return {
                "acronym": acronym,
                "explanation": best_match["target_term"],
                "full_form": best_match.get("context") or best_match["target_term"],
                "source": "glossary",
                "domain": best_match.get("domain"),
                "confidence": best_match["match_score"] / 100,
                "glossary_id": best_match["glossary_id"],
            }

        # Sinon demander à Qwen
        logger.info(f"📚 Absent du glossaire → demande à {self.MODEL_NAME}")

        domain_hint = f" in the field of {domain}" if domain else ""
        context_hint = f"\n\nContext: {context}" if context else ""

        prompt = f"""Explain the acronym "{acronym}"{domain_hint}.
Provide:
1. The full form (what the acronym stands for)
2. A brief 1-sentence explanation

Format your answer as:
Full form: [full form]
Explanation: [explanation]{context_hint}

Answer:"""

        ai_response = self._call_ollama(prompt)
        explanation = self._parse_ai_response(ai_response)

        logger.success(f"✅ Explication AI : {acronym} → {explanation['full_form']}")

        return {
            "acronym": acronym,
            "explanation": explanation["explanation"],
            "full_form": explanation["full_form"],
            "source": "ai",
            "domain": domain,
            "confidence": 0.7,
            "raw_ai_response": ai_response,
        }

    def _parse_ai_response(self, response: str) -> Dict[str, str]:
        lines = response.split('\n')
        full_form = ""
        explanation = ""

        for line in lines:
            line = line.strip()
            if line.lower().startswith("full form:"):
                full_form = line.split(":", 1)[1].strip()
            elif line.lower().startswith("explanation:"):
                explanation = line.split(":", 1)[1].strip()

        if not full_form or not explanation:
            explanation = response.strip()
            full_form = explanation.split('.')[0] if '.' in explanation else explanation

        return {"full_form": full_form, "explanation": explanation}

    async def process_text(
        self,
        text: str,
        domain: Optional[str] = None,
        source_lang: str = "fr",
        target_lang: str = "en",
    ) -> Dict[str, Any]:
        """Extrait et explique tous les acronymes d'un texte."""
        logger.info(f"📄 Traitement acronymes : {len(text)} chars | domaine={domain or 'auto'}")

        acronym_list = self.extract_acronyms(text)

        if not acronym_list:
            logger.warning("⚠️  Aucun acronyme détecté")
            return {"text": text, "acronyms_found": 0, "acronyms": [], "domain": domain}

        explained_acronyms = []

        for acronym in acronym_list:
            context = self._extract_context(text, acronym)
            explanation = await self.explain_acronym(
                acronym=acronym,
                context=context,
                domain=domain,
                source_lang=source_lang,
                target_lang=target_lang,
            )
            explained_acronyms.append(explanation)

        glossary_count = sum(1 for a in explained_acronyms if a['source'] == 'glossary')
        ai_count = sum(1 for a in explained_acronyms if a['source'] == 'ai')
        logger.success(f"✅ {len(explained_acronyms)} acronymes expliqués (glossaire: {glossary_count}, AI: {ai_count})")

        return {
            "text": text,
            "acronyms_found": len(explained_acronyms),
            "acronyms": explained_acronyms,
            "domain": domain,
        }

    def _extract_context(self, text: str, acronym: str, window: int = 100) -> str:
        match = re.search(rf'\b{re.escape(acronym)}\b', text)
        if not match:
            return ""
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        return text[start:end].strip()


_acronym_service: Optional[AcronymService] = None


def get_acronym_service() -> AcronymService:
    global _acronym_service
    if _acronym_service is None:
        _acronym_service = AcronymService()
    return _acronym_service