# MEMORA

<div align="center">

**Your memory, connected.**

Personal AI Memory / Evidence / Context / Action System

---

</div>

## 🚀 Live Demo

**Frontend (Production)**: https://frontend-bhavyarajput0001-bits-projects.vercel.app

> **Note**: Backend is running locally. For full production deployment, see [DEPLOYMENT.md](./DEPLOYMENT.md)

## 📦 GitHub Repository

https://github.com/bhavyarajput0001-bit/memora

---

## What is MEMORA?

MEMORA turns scattered user-provided information into a **searchable, relationship-aware, time-aware, evidence-backed personal memory**.

It is NOT:
- A chatbot
- A file search tool
- A generic RAG app

It IS:
- A memory infrastructure layer
- An evidence-backed reasoning system
- A conflict detection engine
- A provenance-tracked knowledge base

---

## Core Loop

```
INGEST → UNDERSTAND → STORE → CONNECT → RETRIEVE → VERIFY → EXPLAIN → ACT
```

---

## Architecture

### Backend (`backend/`)
- **FastAPI** server with SQLite database
- **SQLAlchemy** models for Documents, Chunks, Entities, Facts, Relationships, Events, Conflicts, Actions
- **TF-IDF retrieval** (scikit-learn) — no local embedding model (8GB RAM constraint)
- **LLM integration** via Hermes router at `localhost:31416`
- **Document parsers**: PDF, TXT, MD, CSV, JSON, EML, PNG, HTML

### Frontend (`frontend/`)
- **Next.js 16** + React 19 + TypeScript
- **Tailwind CSS** with custom MEMORA design system
- **Framer Motion** for animations
- **Lucide React** for icons
- Dark-mode intelligence console aesthetic with glassmorphism UI

### Key Design Decisions
- **SQLite** for local storage (no external DB needed)
- **TF-IDF** instead of embeddings (8GB RAM limit)
- **Hermes router** for LLM access (no API keys required)
- **Single process** deployment (no Docker, no Kubernetes)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.14, FastAPI, SQLAlchemy, SQLite |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind |
| LLM | Hermes Router (localhost:31416) |
| Search | scikit-learn TF-IDF |
| Testing | pytest |
| Deployment | Vercel (frontend), Render/Railway (backend) |

---

## Installation & Setup

### Prerequisites
- Python 3.14+
- Node.js 20+
- npm or pnpm

### Clone Repository
```bash
git clone https://github.com/bhavyarajput0001-bit/memora.git
cd memora
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Variables
Create `.env` in the backend directory:
```bash
MEMORA_DATA_DIR=./data
MEMORA_DB_PATH=./data/memora.db
MEMORA_LLM_BASE_URL=http://localhost:31416/v1
MEMORA_LLM_API_KEY=local-router-key
MEMORA_DEMO_MODE=false
```

---

## Running the Application

### Start Backend
```bash
cd backend
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### Start Frontend
```bash
cd frontend
npx next dev --port 3001
```

### Access the App
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

---

## API Endpoints

### Ingestion
```
POST /api/v1/ingest/file      # Upload document
POST /api/v1/ingest/text      # Ingest raw text
GET  /api/v1/ingest/status    # Get ingestion stats
```

### Query
```
POST /api/v1/query/           # Execute query
```

### Memory
```
GET  /api/v1/memory/          # Get memory summary
GET  /api/v1/memory/documents # List documents
GET  /api/v1/memory/entities  # List entities
GET  /api/v1/memory/facts     # List facts
```

### Timeline
```
GET  /api/v1/timeline/        # Get timeline events
GET  /api/v1/timeline/summary # Get timeline stats
```

### Conflicts
```
GET  /api/v1/conflicts/       # List conflicts
POST /api/v1/conflicts/detect # Run conflict detection
POST /api/v1/conflicts/{id}/resolve  # Resolve conflict
```

### Sources
```
GET  /api/v1/sources/         # List sources
GET  /api/v1/sources/{id}     # Get source details
GET  /api/v1/sources/{id}/chunks  # Get source chunks
```

### Actions
```
POST /api/v1/actions/propose       # Propose action
POST /api/v1/actions/{id}/approve  # Approve action
POST /api/v1/actions/{id}/execute  # Execute action
GET  /api/v1/actions/              # List actions
```

---

## Demo Dataset

Run demo mode to load the Atlas project sample data:
```bash
MEMORA_DEMO_MODE=true python3 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

The demo includes:
- **Project Atlas** — a fictional project with deadlines
- **5 documents** — PDF notes, emails, meeting notes, calendar
- **6 entities** — Rahul, Priya, Karan, Aditi, Neha, Project Atlas
- **9 facts** — including a deliberate conflict (deadline moved from Sep 24 to Sep 26)
- **2 events** — team meeting and demo

---

## Testing

```bash
cd backend
pytest tests/
```

---

## Design System

### Colors (from mockup analysis)
| Name | Hex |
|------|-----|
| Background | #080b14 |
| Sidebar | #0a1020 |
| Content | #0f172a |
| Card | #1e293b |
| Border | #334155 |
| Accent | #06b6d4 |
| Accent Light | #22d3ee |
| Text | #f1f5f9 |
| Text Muted | #94a3b8 |
| Success | #10b981 |
| Warning | #f59e0b |
| Error | #ef4444 |

### Typography
- **Font**: Inter, Plus Jakarta Sans
- **Base size**: 14-16px
- **Hierarchy**: Strong weight differentiation

### Spacing
- **Grid**: 8px
- **Radius**: 10-14px
- **Borders**: 1px subtle

---

## Key Features Implemented

### ✅ Backend
- [x] Document ingestion pipeline
- [x] PDF, TXT, MD, CSV, JSON, EML, PNG, HTML parsers
- [x] Semantic chunking (heading-aware)
- [x] Entity extraction (LLM-powered)
- [x] Fact extraction with provenance
- [x] Event extraction
- [x] TF-IDF hybrid retrieval
- [x] Conflict detection
- [x] Temporal filtering
- [x] Query intent engine
- [x] Grounded answer generation
- [x] Action proposal/approval/execution

### ✅ Frontend
- [x] Dark-mode intelligence console UI
- [x] Glassmorphism design with cyan glow effects
- [x] Left sidebar navigation
- [x] Top bar with search and sync status
- [x] Dashboard with memory overview
- [x] Ask page with chat interface
- [x] Memory database view
- [x] Timeline visualization (Google Calendar-like)
- [x] Conflict detection display
- [x] Source viewer with type panels
- [x] Interactive graph visualization (Obsidian-style)
- [x] Action proposal system
- [x] Upload modals (PDF, Screenshot, Email, Calendar, Notes)

---

## Deployment Guide

### Deploy Backend (Render)

1. Go to https://render.com and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repo: `bhavyarajput0001-bit/memora`
4. Configure:
   - **Name**: memora-backend
   - **Root Directory**: `/`
   - **Runtime**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
5. Add Environment Variables:
   ```
   MEMORA_DEMO_MODE=true
   MEMORA_LLM_BASE_URL=http://localhost:31416/v1
   MEMORA_LLM_API_KEY=local-router-key
   MEMORA_CORS_ORIGINS=*
   ```
6. Click "Create Web Service"
7. Copy the generated URL

### Deploy Frontend (Vercel)

1. Go to https://vercel.com and sign up/login
2. Import your GitHub repo: `bhavyarajput0001-bit/memora`
3. Configure:
   - **Framework**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```
5. Click "Deploy"

See [DEPLOYMENT.md](./DEPLOYMENT.md) for full instructions.

---

## Roadmap

### Phase 9: Testing & Evaluation
- [x] Integration tests for ingestion pipeline
- [x] Evaluation benchmark (50+ test cases)
- [x] End-to-end demo flow tests

### Phase 10: Polish & Deploy
- [x] Security audit
- [x] Performance optimization
- [x] Deployment documentation
- [x] README improvements
- [x] Live deployment

---

## Design Philosophy

> "Make the intelligence visible."

Every AI result must answer three questions visually:
1. **WHAT** does MEMORA think?
2. **WHY** does MEMORA think it?
3. **WHERE** did the information come from?

---

## License

MIT

---

## Acknowledgments

- Hermes Agent for LLM routing
- FastAPI for the backend framework
- Next.js for the frontend
- scikit-learn for TF-IDF retrieval
- Lucide for icons
- Framer Motion for animations
- Vercel for frontend hosting
- Render for backend hosting
