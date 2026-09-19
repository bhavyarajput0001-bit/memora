# MEMORA Backend - Render Deployment Guide

## Deploy to Render (Free Tier)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### Step 2: Connect Repository
1. Click "New +" → "Web Service"
2. Connect your GitHub repo: `bhavyarajput0001-bit/memora`
3. Configure the service:

**Basic Settings:**
- Name: `memora-backend`
- Environment: `Python 3`
- Root Directory: `/`
- Build Command: `pip install -r backend/requirements.txt`
- Start Command: `python -m uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
```
MEMORA_DATABASE_URL=sqlite:///data/memora.db
MEMORA_DEMO_MODE=false
MEMORA_CORS_ORIGINS=*
MEMORA_LLM_BASE_URL=http://localhost:31416/v1
MEMORA_LLM_API_KEY=local-router-key
MEMORA_LLM_MODEL=auto
MEMORA_LLM_MODEL_VISION=auto
```

### Step 3: Storage (Optional)
Add persistent storage for the SQLite database:
- In Render dashboard, go to your service
- Click "Advanced" → "Persistent Volumes"
- Add volume at path: `/data`
- Size: 1GB (free)

### Step 4: Deploy
Click "Create Web Service" and wait for deployment.

## Alternative: Railway

1. Go to https://railway.app
2. Connect GitHub repo
3. Add environment variables
4. Deploy

## Alternative: Fly.io

```bash
fly auth login
fly apps create memora-backend
fly deploy
```

## Post-Deployment

1. Get your Render URL (e.g., `https://memora-backend.onrender.com`)
2. Update frontend `.env.local`:
```
NEXT_PUBLIC_API_URL=https://memora-backend.onrender.com
```
3. Redeploy frontend:
```bash
cd frontend
vercel --prod
```