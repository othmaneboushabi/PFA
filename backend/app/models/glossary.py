"""Modèle de données pour les glossaires terminologiques."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index

from app.core.database import Base


class GlossaryEntry(Base):
    """Entrée de glossaire (terme source → terme cible)."""
    
    __tablename__ = "glossary_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Métadonnées du glossaire
    glossary_name = Column(String(255), nullable=False, index=True)
    glossary_id = Column(String(100), nullable=False, index=True)
    
    # Termes
    source_term = Column(String(500), nullable=False, index=True)
    target_term = Column(String(500), nullable=False)
    
    # Langues
    source_lang = Column(String(10), nullable=False, index=True)
    target_lang = Column(String(10), nullable=False, index=True)
    
    # Contexte optionnel
    context = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Index composé pour recherche rapide
    __table_args__ = (
        Index('idx_glossary_search', 'glossary_id', 'source_lang', 'target_lang'),
    )
    
    def __repr__(self):
        return f"<GlossaryEntry {self.source_term} → {self.target_term}>"