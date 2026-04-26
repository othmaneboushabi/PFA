# Handover Mustapha — Semaine 2 (J12+)

## État actuel du projet (26 avril 2026)

### Ce qui fonctionne

- ✅ **Backend FastAPI** : 6 endpoints opérationnels
- ✅ **ASR** (faster-whisper small) : transcription FR/EN/ES/AR
- ✅ **NER** (spaCy) : extraction entités FR/EN/ES
- ✅ **Traduction** (NLLB-200) : FR↔EN↔ES↔AR avec cache Redis
- ✅ **Infrastructure** : PostgreSQL + Redis via Docker
- ✅ **MVP Streamlit** : interface de démonstration

### Endpoints disponibles

| Méthode | Route | Fonction |
|---------|-------|----------|
| GET | `/` | Page d'accueil |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/version` | Version app |
| POST | `/api/v1/transcribe` | Transcription audio |
| POST | `/api/v1/ner` | Extraction entités |
| POST | `/api/v1/translate` | Traduction multilingue |

### Métriques mesurées

- **ASR** : 4.4s pour 11s audio (RTF 2.5x)
- **NER** : 10-15 ms par texte
- **Traduction** : 1.5s (1ère fois), < 10 ms (cache)

---

## Ce qu'il reste à faire (ta mission)

### J12-J13 : Glossaires terminologiques

**Objectif** : Permettre à l'interprète d'importer ses propres glossaires métier.

**Tâches** :
1. Créer `glossary_service.py` (support CSV, JSON, XLSX, TBX)
2. Intégrer `rapidfuzz` pour fuzzy matching
3. Endpoint `POST /api/v1/glossary/upload`
4. Endpoint `POST /api/v1/glossary/search`

### J14 : Orchestration + métriques

**Objectif** : Pipeline complet ASR → NER + Traduction en parallèle.

**Tâches** :
1. Créer `orchestrator_service.py` (appels async parallèles)
2. Endpoint `POST /api/v1/process` (tout-en-un)
3. Métriques Prometheus sur `/metrics`

### Amélioration qualité traduction (prioritaire)

**Problème actuel** : NLLB-200 donne des traductions moyennes.

**Solution recommandée** : Migration vers **Gemma 2 9B** (tu as un GPU RTX 4060).

**Étapes** :
1. Installer PyTorch avec CUDA : `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
2. Télécharger Gemma 2 9B : voir `docs/migration_gemma.md` (à créer)
3. Modifier `translation_service.py` pour charger Gemma au lieu de NLLB
4. Benchmark sur GPU : latence cible < 1s par traduction

---

## Setup sur ton PC

### Prérequis

- Python 3.11
- Docker Desktop
- Git
- 16 GB RAM + **GPU RTX 4060** (avantage énorme vs Othmane)

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/<username>/ais-pfa.git
cd ais-pfa

# 2. Créer ta branche
git checkout -b mustapha

# 3. Setup backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 4. Copier .env
copy .env.example .env
# Modifier .env : mettre les mots de passe

# 5. Démarrer Docker
cd ..
docker-compose up -d

# 6. Télécharger les modèles spaCy
pip install https://github.com/explosion/spacy-models/releases/download/fr_core_news_lg-3.7.0/fr_core_news_lg-3.7.0-py3-none-any.whl
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1-py3-none-any.whl
pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_lg-3.7.0/es_core_news_lg-3.7.0-py3-none-any.whl

# 7. Télécharger NLLB-200 (ou Gemma si tu migres)
python download_nllb.py

# 8. Lancer le backend
cd backend
uvicorn app.main:app --reload

# 9. Tester
# Ouvrir http://localhost:8000/docs
```

---

## Fichiers importants à connaître

ais-pfa/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # Endpoints FastAPI
│   │   ├── services/         # Logique métier (ASR, NER, Translation)
│   │   ├── schemas/          # Schémas Pydantic (validation)
│   │   ├── core/             # Config + Logging
│   │   └── main.py           # Point d'entrée
│   ├── requirements.txt      # Dépendances Python
│   └── .env                  # Secrets (à créer depuis .env.example)
├── docker-compose.yml        # PostgreSQL + Redis
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   ├── benchmarks.md         # Mesures de performance
│   └── TROUBLESHOOTING.md    # Solutions aux problèmes connus
└── scripts/
└── streamlit_mvp.py      # Interface de démo
