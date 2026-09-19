# MEMORA Deployment Guide — What You Need

## 1. Render (Backend) — FREE

### What You Need:
- **GitHub Account** → https://github.com/signup (free)
- **Render Account** → https://render.com/signup (free, connects with GitHub)

### Steps:
1. Sign up at https://render.com (use "Continue with GitHub")
2. Click "New +" → "Web Service"
3. Connect your repo: `bhavyarajput0001-bit/memora`
4. Fill in:
   - **Name**: `memora-backend`
   - **Root Directory**: `/`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python -m uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Add Environment Variables:
   ```
   MEMORA_DATABASE_URL=sqlite:///data/memora.db
   MEMORA_DEMO_MODE=false
   MEMORA_CORS_ORIGINS=*
   MEMORA_LLM_BASE_URL=http://localhost:31416/v1
   MEMORA_LLM_API_KEY=local-router-key
   MEMORA_LLM_MODEL=auto
   MEMORA_LLM_MODEL_VISION=auto
   ```
6. Click "Create Web Service"

### Free Tier Limits:
- 750 hours/month (enough for 1 app running 24/7)
- Spins down after 15 min idle (first request takes ~30s to wake)
- 512MB RAM
- SQLite database (persists for 24h after last request)

---

## 2. Vercel (Frontend) — ALREADY DONE ✅

Your frontend is already deployed at:
https://frontend-rfqze98z1-bhavyarajput0001-bits-projects.vercel.app

If you need to update it after backend deployment:
```bash
cd "/Users/bhavyarajput/Library/Mobile Documents/com~apple~CloudDocs/memora/frontend"
vercel --prod
```

---

## 3. Railway (Alternative Backend) — FREE TIER

### What You Need:
- **Railway Account** → https://railway.app/signup (free, $5/month credit)

### Steps:
1. Sign up at https://railway.app (use "Continue with GitHub")
2. Click "New Project" → "Deploy from GitHub repo"
3. Select: `bhavyarajput0001-bit/memora`
4. Railway auto-detects Python. Set these env vars:
   ```
   MEMORA_DATABASE_URL=sqlite:///data/memora.db
   MEMORA_DEMO_MODE=false
   MEMORA_CORS_ORIGINS=*
   MEMORA_LLM_BASE_URL=http://localhost:31416/v1
   MEMORA_LLM_API_KEY=local-router-key
   ```
5. Click "Deploy"

### Free Tier:
- $5/month free credit
- Dies after 7 days inactivity (easy to restart)

---

## 4. Supabase (Database for Multi-Device) — FREE

### What You Need:
- **Supabase Account** → https://supabase.com/dashboard/signup (free)

### Steps:
1. Sign up at https://supabase.com
2. Click "New Project"
3. Fill in:
   - **Organization**: Create new or select existing
   - **Project name**: `memora`
   - **Database password**: Generate random or set your own
   - **Region**: Closest to you (e.g., `Singapore (sgp1)`)
4. Wait 2-3 minutes for setup
5. Go to Project Settings → Database
6. Copy the connection string:
   ```
   postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
   ```

### Free Tier:
- 500MB database
- Unlimited API requests
- Auth included (for user login later)

---

## 5. GitHub — ALREADY HAVE ✅

Your repo is public at:
https://github.com/bhavyarajput0001-bit/memora

---

## Summary Checklist

| Platform | Status | Link |
|----------|--------|------|
| GitHub | ✅ Have | github.com/bhavyarajput0001-bit/memora |
| Vercel | ✅ Deployed | frontend-rfqze98z1-...vercel.app |
| Render | ⏳ Need Account | render.com |
| Railway | ⏳ Alternative | railway.app |
| Supabase | ⏳ Optional (for Phase 5) | supabase.com |

---

## Quick Start (Recommended)

1. **Render for backend**: https://render.com/signup → connect GitHub → deploy
2. **After deployment**: Update frontend env with new backend URL
3. **Test**: Open the Vercel URL and try querying

---

## After Backend is Live

Update your frontend `.env.local`:
```
NEXT_PUBLIC_API_URL=https://memora-backend.onrender.com
```

Then redeploy frontend:
```bash
cd "/Users/bhavyarajput/Library/Mobile Documents/com~apple~CloudDocs/memora/frontend"
vercel --prod
```

---

## Environment Variables Reference

Copy these to Render/Railway:

```env
# Database
MEMORA_DATABASE_URL=sqlite:///data/memora.db

# LLM (Hermes Router)
MEMORA_LLM_BASE_URL=http://localhost:31416/v1
MEMORA_LLM_API_KEY=local-router-key
MEMORA_LLM_MODEL=auto
MEMORA_LLM_MODEL_VISION=auto

# App
MEMORA_DEMO_MODE=false
MEMORA_CORS_ORIGINS=*
```

Note: For production, you'll need to run Hermes router on a server or use an API-based LLM instead of localhost:31416.

---

## Hermes Router Note

Currently MEMORA uses Hermes router at `localhost:31416`. For production:

**Option A**: Deploy Hermes router separately (complex)
**Option B**: Use OpenAI/other API directly

To use OpenAI:
```env
MEMORA_LLM_BASE_URL=https://api.openai.com/v1
MEMORA_LLM_API_KEY=sk-your-openai-key
MEMORA_LLM_MODEL=gpt-4o-mini
```

To use any OpenAI-compatible provider (OpenRouter, etc.):
```env
MEMORA_LLM_BASE_URL=https://openrouter.ai/api/v1
MEMORA_LLM_API_KEY=sk-or-your-key
MEMORA_LLM_MODEL=google/gemini-2.0-flash-001
```