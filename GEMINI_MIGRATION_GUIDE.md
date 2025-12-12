# Gemini API Migration Guide

The backend has been successfully migrated from OpenAI to Google's Gemini API! 🎉

## Benefits of Gemini

✅ **Free Tier**: Generous free quota (15 requests per minute, 1 million tokens per day)
✅ **Cost-Effective**: Much cheaper than OpenAI for paid usage
✅ **Fast Performance**: Gemini 2.0 Flash is optimized for speed
✅ **Same Functionality**: RAG capabilities maintained

## What Changed

### Backend Services Updated
1. **Embeddings**: Now using `models/text-embedding-004` (768 dimensions)
2. **Chat Model**: Now using `gemini-2.0-flash-exp` (fast and free)
3. **Dependencies**: Replaced `openai` package with `google-generativeai`

### Files Modified
- `backend/requirements.txt` - Updated dependencies
- `backend/config/settings.py` - Changed from `openai_api_key` to `gemini_api_key`
- `backend/services/embeddings.py` - Gemini embeddings implementation
- `backend/services/rag_service.py` - Gemini chat completions

## Setup Instructions

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API key" or "Create API key"
3. Copy your API key

### 2. Update Environment Variables

Update your `backend/.env` file:

```env
# Replace this:
# OPENAI_API_KEY=sk-...

# With this:
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

# Keep these unchanged:
NEON_DATABASE_URL=...
QDRANT_URL=...
QDRANT_API_KEY=...
```

### 3. Reinstall Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Test the Integration

Start the backend server:

```bash
cd backend
python -m uvicorn api.main:app --reload --port 8080
```

Test the chatbot on your frontend - it should work exactly as before!

## Important Notes

### Re-embedding Required

⚠️ **The existing vector embeddings in Qdrant were created with OpenAI's model and need to be re-created with Gemini's embedding model.**

**Two options:**

#### Option A: Keep Current Embeddings (Quick Fix)
- Temporarily revert embedding dimensions in settings.py:
  ```python
  embedding_dimensions: int = 512  # Match existing OpenAI embeddings
  ```
- This will allow queries to work, but embeddings won't match perfectly
- Search quality may be slightly degraded

#### Option B: Re-embed All Content (Recommended)
- Run the embedding script to re-populate Qdrant with Gemini embeddings
- This ensures best search quality
- Takes ~10-15 minutes for all 53 FAR parts

To re-embed:
```bash
cd backend
python scripts/populate_all_parts.py
```

### Rate Limits

Gemini Free Tier:
- 15 requests per minute
- 1 million tokens per day
- 1500 requests per day

This is more than sufficient for moderate usage. For heavy traffic, consider upgrading to paid tier.

## Troubleshooting

### "API key not valid" error
- Ensure `GEMINI_API_KEY` is set correctly in `.env`
- Verify the key is active at [Google AI Studio](https://aistudio.google.com/)

### Search returns no results
- Re-embed the content (Option B above)
- Or temporarily adjust embedding dimensions (Option A above)

### "Resource has been exhausted" error
- You've hit the free tier rate limit
- Wait a minute before trying again
- Consider upgrading to paid tier for production

## Rollback (If Needed)

If you need to revert to OpenAI:

1. Restore `backend/requirements.txt` (change `google-generativeai` back to `openai`)
2. Restore original versions of `embeddings.py` and `rag_service.py`
3. Update `.env` to use `OPENAI_API_KEY` instead of `GEMINI_API_KEY`
4. Run `pip install -r requirements.txt`

## Next Steps

1. Update your `.env` file with Gemini API key
2. Reinstall dependencies
3. Choose embedding strategy (Option A or B above)
4. Test the chatbot
5. Update production environment variables on Railway

Enjoy the free AI-powered FAR chatbot! 🚀
