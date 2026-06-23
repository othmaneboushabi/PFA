# 🎙️ AIS — Assistant Interprète Simultané

> Système intelligent d'aide à l'interprétation simultanée multilingue  
> Transcription · Traduction · NER · Streaming Temps Réel

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![License](https://img.shields.io/badge/License-MIT-yellow)
![EMSI](https://img.shields.io/badge/EMSI-PFA%202026-red)

---

## 📋 Description

**AIS (Assistant Interprète Simultané)** est un système complet d'aide à
l'interprétation simultanée développé dans le cadre du **Projet de Fin
d'Années (PFA)** à l'EMSI Rabat, au sein du **SmartILab / ACM Chapter**,
sous la supervision de **Dr. Hasnaa Chaabi**.

Le système fonctionne **entièrement en local** — aucune donnée ne quitte
le PC de l'utilisateur, garantissant une confidentialité totale.

---

## ✨ Fonctionnalités

| Fonctionnalité | Description | Technologie |
|---------------|-------------|-------------|
| 🎤 Transcription ASR | 4 langues (FR, EN, ES, AR) — 97% précision | faster-Whisper |
| 🌍 Traduction | Contextuelle, multilingue, locale | Qwen 2.5 7B |
| 🏷️ NER | Extraction entités (PER, LOC, ORG) | spaCy + CAMeL BERT |
| 📚 Glossaires | Import CSV/JSON/XLSX + fuzzy search | PostgreSQL + rapidfuzz |
| ⚡ Temps Réel | Streaming WebSocket microphone | WebSocket |
| 📝 Résumé | Résumé automatique en points clés | Qwen 2.5 7B |
| 🔤 Acronymes | Détection + explication multilingue | Hybride |
| 💾 Cache | Traductions mémorisées 7 jours | Redis |

---

## 🏗️ Architecture
Frontend React 18 (port 5173)

↕ HTTP/REST + WebSocket

Backend FastAPI (port 8000)

↕ HTTP local / asyncpg / redis-py

Services IA : Whisper · spaCy · CAMeL BERT · Qwen 2.5 7B

↕

Infrastructure : PostgreSQL · Redis · Docker · Ollama
---

## 🚀 Installation

### Prérequis

- Python 3.13+
- Node.js 18+
- Docker Desktop
- Ollama

### 1. Cloner le projet

```bash
git clone https://github.com/othmaneboushabi/PFA.git
cd PFA
```

### 2. Lancer l'infrastructure

```bash
docker-compose up -d
```

### 3. Installer le backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 4. Télécharger les modèles spaCy

```bash
python -m spacy download fr_core_news_lg
python -m spacy download en_core_web_lg
python -m spacy download es_core_news_lg
```

### 5. Télécharger Qwen 2.5 7B

```bash
ollama pull qwen2.5:7b
```

### 6. Lancer le backend

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 7. Installer et lancer le frontend

```bash
cd ../frontend
npm install
npm run dev
```

### 8. Accéder à l'application

| Service | URL |
|---------|-----|
| 🌐 Frontend | http://localhost:5173 |
| 📡 API Swagger | http://localhost:8000/docs |
| 🗄️ PostgreSQL | localhost:5433 |
| 💾 Redis | localhost:6379 |

---

## 🛠️ Stack Technique

### Backend
| Composant | Technologie | Version |
|-----------|-------------|---------|
| Framework API | FastAPI + Uvicorn | 0.115+ |
| ASR | faster-Whisper | 1.1+ |
| NER FR/EN/ES | spaCy | 3.8+ |
| NER Arabe | CAMeL BERT | 4.40+ |
| LLM | Qwen 2.5 7B via Ollama | 2.5 |
| Base de données | PostgreSQL | 16 |
| Cache | Redis | 7 |
| Conteneurisation | Docker Compose | 2.x |

### Frontend
| Composant | Technologie | Version |
|-----------|-------------|---------|
| Framework | React | 18 |
| Bundler | Vite | 8.x |
| Langage | JavaScript ES2023 | — |

---

## 📁 Structure du projet
PFA/

├── backend/

│   ├── app/

│   │   ├── main.py

│   │   ├── services/

│   │   │   ├── asr_service.py

│   │   │   ├── ner_service.py

│   │   │   ├── translation_service.py

│   │   │   ├── glossary_service.py

│   │   │   ├── acronym_service.py

│   │   │   ├── orchestrator_service.py

│   │   │   └── streaming_service.py

│   │   └── routers/

│   ├── requirements.txt

│   └── .env

├── frontend/

│   ├── src/

│   │   ├── App.jsx

│   │   ├── pages/

│   │   │   ├── LandingPage.jsx

│   │   │   ├── RealtimePage.jsx

│   │   │   ├── BatchPage.jsx

│   │   │   ├── GlossaryPage.jsx

│   │   │   └── ToolsPage.jsx

│   │   ├── components/

│   │   │   └── EntityBadge.jsx

│   │   └── services/

│   │       └── api.js

│   └── package.json

├── docker-compose.yml

└── README.md
---

## 📊 Performances

| Métrique | Résultat |
|----------|---------|
| Précision ASR (FR) | 95.9% |
| Précision ASR (AR) | 97.18% |
| Précision NER (FR) | 90%+ |
| Précision NER (AR) | 88%+ |
| Cache Redis (hit) | < 10ms |
| Gain cache | 400x |
| Latence pipeline | -37% (asyncio) |

---

## 👥 Auteurs

| Nom | Rôle |
|-----|------|
| **Othmane Boushabi** | Développeur Full-Stack IA |
| **Mustapha Hamdaoui Alaoui** | Développeur Full-Stack IA |

**Encadrante :** Dr. Hasnaa Chaabi  
**Structure :** SmartILab / ACM Chapter — EMSI Rabat  
**Année :** 2025/2026

---

## 📄 Licence

Ce projet est développé dans le cadre académique de l'EMSI Rabat.  
© 2026 Othmane Boushabi & Mustapha Hamdaoui Alaoui