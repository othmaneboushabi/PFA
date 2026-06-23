"""Service de gestion des glossaires terminologiques avec PostgreSQL."""
import csv
import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from io import StringIO

from rapidfuzz import fuzz, process
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import openpyxl

from app.models.glossary import GlossaryEntry
from app.core.database import AsyncSessionLocal


class GlossaryService:
    """Service de gestion des glossaires (PostgreSQL)."""
    
    SUPPORTED_FORMATS = ["csv", "json", "xlsx", "tbx"]
    DEFAULT_FUZZY_THRESHOLD = 80
    
    def __init__(self):
        """Initialise le service de glossaires."""
        logger.info("GlossaryService initialisé (PostgreSQL)")
    
    def parse_csv(self, content: bytes, glossary_name: str) -> List[Dict[str, Any]]:
        """Parse un fichier CSV."""
        entries = []
        text = content.decode('utf-8')
        reader = csv.DictReader(StringIO(text))
        
        for row in reader:
            entry = {
                "glossary_name": glossary_name,
                "source_term": row.get("source_term", "").strip(),
                "target_term": row.get("target_term", "").strip(),
                "source_lang": row.get("source_lang", "fr").strip(),
                "target_lang": row.get("target_lang", "en").strip(),
                "context": row.get("context", "").strip(),
                "domain": row.get("domain", "").strip(),
            }
            
            if entry["source_term"] and entry["target_term"]:
                entries.append(entry)
        
        logger.info(f"✅ CSV parsé : {len(entries)} entrées")
        return entries
    
    def parse_json(self, content: bytes, glossary_name: str) -> List[Dict[str, Any]]:
        """Parse un fichier JSON."""
        data = json.loads(content.decode('utf-8'))
        entries = []
        
        for item in data:
            entry = {
                "glossary_name": glossary_name,
                "source_term": item.get("source", item.get("source_term", "")).strip(),
                "target_term": item.get("target", item.get("target_term", "")).strip(),
                "source_lang": item.get("source_lang", "fr").strip(),
                "target_lang": item.get("target_lang", "en").strip(),
                "context": item.get("context", "").strip(),
                "domain": item.get("domain", "").strip(),
            }
            
            if entry["source_term"] and entry["target_term"]:
                entries.append(entry)
        
        logger.info(f"✅ JSON parsé : {len(entries)} entrées")
        return entries
    
    def parse_xlsx(self, content: bytes, glossary_name: str) -> List[Dict[str, Any]]:
        """Parse un fichier Excel (.xlsx)."""
        from io import BytesIO
        
        workbook = openpyxl.load_workbook(BytesIO(content))
        sheet = workbook.active
        
        entries = []
        headers = [cell.value for cell in sheet[1]]
        
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_dict = dict(zip(headers, row))
            
            entry = {
                "glossary_name": glossary_name,
                "source_term": str(row_dict.get("source_term", "")).strip(),
                "target_term": str(row_dict.get("target_term", "")).strip(),
                "source_lang": str(row_dict.get("source_lang", "fr")).strip(),
                "target_lang": str(row_dict.get("target_lang", "en")).strip(),
                "context": str(row_dict.get("context", "")).strip(),
                "domain": str(row_dict.get("domain", "")).strip(),
            }
            
            if entry["source_term"] and entry["target_term"]:
                entries.append(entry)
        
        logger.info(f"✅ XLSX parsé : {len(entries)} entrées")
        return entries
    
    async def upload_glossary(
        self,
        file_content: bytes,
        filename: str,
        format_type: str,
    ) -> Dict[str, Any]:
        """Upload et sauvegarde un glossaire dans PostgreSQL."""
        if format_type not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Format '{format_type}' non supporté. "
                f"Formats supportés : {self.SUPPORTED_FORMATS}"
            )
        
        glossary_name = Path(filename).stem
        glossary_id = str(uuid.uuid4())[:8]
        
        logger.info(f"📥 Upload glossaire : {filename} ({format_type})")
        
        # Parse selon le format
        if format_type == "csv":
            entries = self.parse_csv(file_content, glossary_name)
        elif format_type == "json":
            entries = self.parse_json(file_content, glossary_name)
        elif format_type == "xlsx":
            entries = self.parse_xlsx(file_content, glossary_name)
        elif format_type == "tbx":
            raise NotImplementedError("Format TBX pas encore implémenté")
        
        # Sauvegarder dans PostgreSQL
        async with AsyncSessionLocal() as session:
            for entry_data in entries:
                entry = GlossaryEntry(
                    glossary_id=glossary_id,
                    glossary_name=entry_data["glossary_name"],
                    source_term=entry_data["source_term"],
                    target_term=entry_data["target_term"],
                    source_lang=entry_data["source_lang"],
                    target_lang=entry_data["target_lang"],
                    context=entry_data.get("context"),
                    domain=entry_data.get("domain"),
                )
                session.add(entry)
            
            await session.commit()
        
        logger.success(
            f"✅ Glossaire '{glossary_name}' sauvegardé : {len(entries)} entrées | ID={glossary_id}"
        )
        
        return {
            "glossary_id": glossary_id,
            "glossary_name": glossary_name,
            "entries_count": len(entries),
            "format": format_type,
        }
    
    async def search_term(
        self,
        term: str,
        source_lang: str = "fr",
        target_lang: str = "en",
        glossary_id: Optional[str] = None,
        fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """Recherche un terme dans PostgreSQL."""
        logger.info(
            f"🔍 Recherche : '{term}' | {source_lang}→{target_lang} | "
            f"glossary={glossary_id or 'ALL'}"
        )
        
        async with AsyncSessionLocal() as session:
            # Construire la requête
            query = select(GlossaryEntry).where(
                GlossaryEntry.source_lang == source_lang,
                GlossaryEntry.target_lang == target_lang,
            )
            
            if glossary_id:
                query = query.where(GlossaryEntry.glossary_id == glossary_id)
            
            result = await session.execute(query)
            candidates = result.scalars().all()
        
        if not candidates:
            logger.warning(f"⚠️  Aucune entrée trouvée pour {source_lang}→{target_lang}")
            return []
        
        # Fuzzy matching
        source_terms = [c.source_term for c in candidates]
        matches = process.extract(
            term,
            source_terms,
            scorer=fuzz.ratio,
            limit=5,
        )
        
        # Filtrer et enrichir
        results = []
        for matched_term, score, idx in matches:
            if score >= fuzzy_threshold:
                entry = candidates[idx]
                results.append({
                    "glossary_id": entry.glossary_id,
                    "glossary_name": entry.glossary_name,
                    "source_term": entry.source_term,
                    "target_term": entry.target_term,
                    "source_lang": entry.source_lang,
                    "target_lang": entry.target_lang,
                    "context": entry.context,
                    "domain": entry.domain,
                    "match_score": int(score),
                    "matched_as": matched_term,
                })
        
        logger.info(f"✅ {len(results)} résultats trouvés (seuil={fuzzy_threshold})")
        
        return results


# Singleton
_glossary_service: Optional[GlossaryService] = None


def get_glossary_service() -> GlossaryService:
    """Retourne l'instance unique du service de glossaires."""
    global _glossary_service
    if _glossary_service is None:
        _glossary_service = GlossaryService()
    return _glossary_service