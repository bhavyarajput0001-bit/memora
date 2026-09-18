# MEMORA Deployment Guide

## Architecture
- **Frontend**: Next.js 16 (Vercel)
- **Backend**: FastAPI (Render/Railway)
- **Database**: SQLite (embedded)

## Deploy Backend (Render)

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
7. Copy the generated URL (e.g., `https://memora-backend.onrender.com`)

## Deploy Frontend (Vercel)

1. Go to https://vercel.com and sign up/login
2. Import your GitHub repo: `bhavyarajput0001-bit/memora`
3. Configure:
   - **Framework**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://memora-backend.onrender.com
   ```
5. Click "Deploy"

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/ingest/file` - Upload document
- `POST /api/v1/ingest/text` - Ingest text
- `GET /api/v1/memory/` - Get memory stats
- `POST /api/v1/query/` - Query memory
- `GET /api/v1/sources/` - List sources
- `GET /api/v1/documents/` - List documents
- `POST /api/v1/documents/search` - Search documents

## Notes

- Backend uses SQLite (file-based database)
- Demo mode seeds sample data on startup
- LLM router runs locally on port 31416 (optional for basic features)
- CORS is enabled for all origins in production
