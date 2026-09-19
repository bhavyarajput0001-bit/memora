# MEMORA Backend - Render Deployment

## Quick Deploy to Render
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repo: `bhavyarajput0001-bit/memora`
4. Configure:
   - **Name**: memora-backend
   - **Root Directory**: `/`
   - **Runtime**: Docker
   - **Docker Context**: `/`
   - **Dockerfile**: `Dockerfile`
5. Add Environment Variables:
   ```
   MEMORA_DEMO_MODE=false
   MEMORA_CORS_ORIGINS=*
   MEMORA_LLM_BASE_URL=http://localhost:31416/v1
   MEMORA_LLM_API_KEY=local-router-key
   MEMORA_DATABASE_URL=sqlite:///data/memora.db
   ```
6. Click "Create Web Service"

## Alternative: Python Runtime (without Docker)
If you want to use Python runtime instead:
- **Build Command**: `pip install -r backend/requirements.prod.txt`
- **Start Command**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

## Notes
- Render free tier spins down after 15 min of inactivity (first request takes ~30s)
- Use a ping service to keep alive: https://cron-job.org
- Database is SQLite file at `data/memora.db`
- For persistent storage, upgrade to Render Postgres ($7/mo)

## Frontend Connection
Update `.env.local` in frontend:
```
NEXT_PUBLIC_API_URL=https://memora-backend.onrender.com
```