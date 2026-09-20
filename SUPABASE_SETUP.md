# MEMORA Supabase Setup Guide

## Step 1: Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Sign up/log in with GitHub
3. Click "New Project"
4. Fill in:
   - **Organization**: Create new (or select existing)
   - - **Project name**: `memora`
   - **Database password**: Click "Generate" (save this!)
   - **Region**: Pick closest to you (e.g., Singapore for Asia, Frankfurt for Europe)
   - **Wait 2-3 minutes for setup**

5. Click "Create new project"

## Step 2: Get Connection String

1. Go to Project Settings → Database
2. Scroll down to "Connection string"
3. Select "URI" tab
4. Copy the connection string:
   ```
   postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
   ```
   
   Example:
   ```
   postgresql://postgres.abc123xyz:MyPassword123!@db.abc123xyz.supabase.co:5432/postgres
   ```

## Step 3: Run Migration

1. Go to SQL Editor in Supabase dashboard
2. Copy the contents of `database/migrations/001_initial_schema.sql`
3. Paste and run

## Step 4: Update Environment Variables

Add these to your deployment:

### For Render:
Go to Dashboard → Your Service → Environment Variables:
```
MEMORA_DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
MEMORA_DEMO_MODE=false
MEMORA_CORS_ORIGINS=*
MEMORA_LLM_BASE_URL=http://localhost:31416/v1
MEMORA_LLM_API_KEY=local-router-key
MEMORA_LLM_MODEL=auto
MEMORA_LLM_MODEL_VISION=auto
```

### For Railway:
Go to Project → Variables:
```
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
MEMORA_DEMO_MODE=false
MEMORA_CORS_ORIGINS=*
MEMORA_LLM_BASE_URL=http://localhost:31416/v1
MEMORA_LLM_API_KEY=local-router-key
```

## Step 5: Redeploy

After adding environment variables, redeploy your service.

---

## What Changes with Supabase

| Feature | SQLite | Supabase |
|---------|--------|----------|
| Multi-device sync | ❌ No | ✅ Yes |
| User authentication | ❌ No | ✅ Yes (built-in) |
| Real-time subscriptions | ❌ No | ✅ Yes |
| API automatically | ❌ No | ✅ Yes (REST + GraphQL) |
| Backup/restore | Manual | Automatic |
| Cost | Free | $0 (500MB free tier) |

---

## Optional: Enable Supabase Auth

If you want user authentication:

1. Go to Authentication → Providers
2. Enable "Email" provider
3. Go to SQL Editor and run:
```sql
-- Create API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    key VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used TIMESTAMPTZ
);
```

4. Generate API key for your app:
```sql
INSERT INTO api_keys (user_id, key, name)
SELECT id, 'sk-memora-' || gen_random_uuid()::text, 'Main App'
FROM auth.users
WHERE email = 'your@email.com'
LIMIT 1;
```

---

## Testing the Connection

After deployment, test:
```bash
# Health check
curl https://your-backend.onrender.com/health

# Should return:
# {"status":"healthy","service":"MEMORA","version":"1.0.0"}
```