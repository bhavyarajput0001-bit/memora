# MEMORA - Deployment Guide

## Prerequisites

### System Requirements
- **OS**: macOS, Linux, or Windows (WSL2)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 5GB free space
- **Node.js**: 18+ (for frontend)
- **Python**: 3.10+ (for backend)

### Required API Keys
Set up these environment variables:
```bash
# LLM Router (Hermes)
MEMORA_LLM_BASE_URL=http://localhost:31416/v1
MEMORA_LLM_API_KEY=your-api-key-here
MEMORA_LLM_MODEL_FAST=deepseek-v4-flash
MEMORA_LLM_MODEL_STRONG=nemotron-3-ultra-550b

# Optional: Embeddings (disabled by default for 8GB RAM)
MEMORA_EMBEDDING_ENABLED=false

# Optional: Database (SQLite by default)
MEMORA_DB_PATH=/path/to/memora.db
MEMORA_DATA_DIR=/path/to/data
```

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-org/memora.git
cd memora
```

### 2. Install Backend Dependencies
```bash
cd backend
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd ../frontend
npm install
# or
pnpm install
```

### 4. Initialize Database
```bash
cd ../backend
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -c "from backend.db import init_db; init_db()"
```

## Running Locally

### Backend (Terminal 1)
```bash
cd /path/to/memora/backend
MEMORA_DEMO_MODE=true \
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m uvicorn app:app \
  --host 127.0.0.1 \
  --port 8000 \
  --reload
```

### Frontend (Terminal 2)
```bash
cd /path/to/memora/frontend
npm run dev
# or
pnpm dev
```

### Access the Application
- **Frontend**: http://localhost:3001
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

## Production Deployment

### Option 1: Docker (Recommended)
```bash
# Build images
docker build -t memora-backend ./backend
docker build -t memora-frontend ./frontend

# Run with docker-compose
docker-compose up -d
```

### Option 2: Vercel + Railway
```bash
# Frontend to Vercel
cd frontend
vercel --prod

# Backend to Railway/Render
cd ../backend
railway up
```

### Environment Variables for Production
```bash
# Backend
MEMORA_DEMO_MODE=false
MEMORA_HOST=0.0.0.0
MEMORA_PORT=8000
MEMORA_CORS_ORIGINS=https://your-domain.com

# Database (PostgreSQL)
MEMORA_DB_PATH=postgresql://user:pass@host:5432/memora

# Embeddings (optional)
MEMORA_EMBEDDING_ENABLED=true
MEMORA_EMBEDDING_MODEL=text-embedding-3-small
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Memory
```bash
GET /api/v1/memory/           # Get memory stats
GET /api/v1/memory/entities   # List entities
GET /api/v1/memory/facts      # List facts
```

### Timeline
```bash
GET /api/v1/timeline/?days=30&limit=50
```

### Conflicts
```bash
GET /api/v1/conflicts/?status=all
POST /api/v1/conflicts/detect
```

### Sources
```bash
GET /api/v1/sources/
GET /api/v1/sources/{doc_id}
GET /api/v1/sources/{doc_id}/chunks
```

### Query
```bash
POST /api/v1/query/
{
  "question": "What is the latest deadline?"
}
```

### Actions
```bash
GET /api/v1/actions/
POST /api/v1/actions/propose
POST /api/v1/actions/{id}/approve
POST /api/v1/actions/{id}/execute
```

### Ingestion
```bash
POST /api/v1/ingest/file    # Upload file
POST /api/v1/ingest/text    # Ingest text
```

## Testing

### Run Evaluation Benchmark
```bash
cd tests
python test_evaluation.py
```

### Run Security Tests
```bash
python test_security.py
```

### Run All Tests
```bash
pytest tests/ -v
```

## Troubleshooting

### Backend Not Starting
```bash
# Check Python version
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Build Fails
```bash
# Clear cache
rm -rf .next
npm cache clean --force
npm install
```

### API Connection Issues
```bash
# Check if backend is running
curl http://127.0.0.1:8000/health

# Check port availability
lsof -i :8000
```

## Architecture

```
memora/
├── backend/              # FastAPI backend
│   ├── api/routes/      # REST endpoints
│   ├── services/        # Business logic
│   ├── parsers/         # Document parsers
│   ├── models/          # SQLAlchemy models
│   └── config.py        # Configuration
├── frontend/            # Next.js 16 frontend
│   ├── app/            # Pages
│   ├── components/     # React components
│   └── lib/            # Utilities & API client
├── tests/              # Test suites
└── docs/               # Documentation
```

## License
MIT License - See LICENSE file for details

## Support
- GitHub Issues: https://github.com/your-org/memora/issues
- Documentation: https://memora.dev/docs
