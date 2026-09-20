# MEMORA LLM Provider Configuration

## Current Setup (Default)
MEMORA currently uses the local Hermes router at `http://localhost:31416/v1` with API key `local-router-key`.
This gives you access to models like:
- auto/coding:free
- deepseek-v4-flash
- nemotron-3-ultra-550b
- claude-sonnet-4-5
- claude-haiku-4-5

## Option 1: Use NVIDIA API (Already Configured ✅)

Your NVIDIA API key is already in the Hermes config. Use it directly:

### Environment Variables:
```env
MEMORA_LLM_BASE_URL=https://integrate.api.nvidia.com/v1
MEMORA_LLM_API_KEY=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
MEMORA_LLM_MODEL=nvidia/nemotron-3-ultra-550b-a55b
MEMORA_LLM_MODEL_FAST=nvidia/nemotron-3-ultra-550b-a55b
MEMORA_LLM_MODEL_STRONG=nvidia/nemotron-3-ultra-550b-a55b
MEMORA_LLM_MODEL_VISION=nvidia/llama-3.2-11b-vision-instruct
```

### Available NVIDIA Models:
- `nvidia/nemotron-3-ultra-550b-a55b` (best all-around)
- `nvidia/llama-3.1-nemotron-70b-instruct` (good balance)
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` (reasoning)
- `cuda/neural-chat-7b` (fast, small)

## Option 2: Switch to OpenRouter

OpenRouter provides access to many open-source and proprietary models.

### Step 1: Get OpenRouter API Key
1. Go to https://openrouter.ai/keys
2. Sign up or log in
3. Create a new key

### Step 2: Update Environment Variables
```env
MEMORA_LLM_BASE_URL=https://openrouter.ai/api/v1
MEMORA_LLM_API_KEY=sk-or-your-key-here
MEMORA_LLM_MODEL=google/gemini-2.0-flash-001
```

## Option 3: Continue Using Hermes Router (Local)

The Hermes router is already running at localhost:31416 and provides excellent free models.

### Environment Variables:
```env
MEMORA_LLM_BASE_URL=http://localhost:31416/v1
MEMORA_LLM_API_KEY=local-router-key
MEMORA_LLM_MODEL=auto
```

## Recommendation

**Use NVIDIA API** - It's already configured and provides excellent reasoning models at no cost.

### For Production Deployment:
1. Add the NVIDIA env vars to your backend deployment (Render/Railway)
2. Restart the service
3. Test with: `curl -X POST <your-api>/api/v1/query -d '{"query":"hello"}'`

## Testing the Connection

```bash
# Test NVIDIA API
curl -s -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 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" \
  -d '{"model":"nvidia/nemotron-3-ultra-550b-a55b","messages":[{"role":"user","content":"hi"}],"max_tokens":20}' \
  --max-time 30

# Expected: JSON response with model="nvidia/nemotron-3-ultra-550b-a55b"
```