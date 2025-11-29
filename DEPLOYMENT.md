# Deployment Guide

This guide covers deploying the FAR Reference Book to production.

## Architecture

- **Frontend**: Docusaurus static site → Vercel/Netlify
- **Backend**: FastAPI Python app → Railway/Render
- **Vector DB**: Qdrant Cloud (already configured)
- **SQL DB**: PostgreSQL on Supabase/Neon

## Quick Deploy Options

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Frontend (Vercel)
1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Vercel will auto-detect Docusaurus
5. Add environment variable:
   - `REACT_APP_BACKEND_URL` = your Railway backend URL

#### Backend (Railway)
1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will detect the `railway.json` config
5. Add environment variables (from `.env.example`):
   - `OPENAI_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
   - `DATABASE_URL`
   - `CORS_ORIGINS` (set to your Vercel URL)
6. Deploy!

### Option 2: Netlify (Frontend) + Render (Backend)

#### Frontend (Netlify)
1. Push to GitHub
2. Go to [netlify.com](https://netlify.com)
3. "Add new site" → "Import an existing project"
4. Build settings:
   - Build command: `npm run build`
   - Publish directory: `build`
5. Add environment variable:
   - `REACT_APP_BACKEND_URL` = your Render backend URL

#### Backend (Render)
1. Go to [render.com](https://render.com)
2. "New" → "Web Service"
3. Connect your GitHub repository
4. Render will detect `render.yaml`
5. Add environment variables
6. Deploy!

## Database Setup

### PostgreSQL (Supabase - Recommended)
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Copy the connection string
4. Run migrations:
   ```bash
   # In your backend directory
   python -m alembic upgrade head
   ```

## Vector Database (Already Set Up)

Your Qdrant Cloud instance is already configured. Just add these env vars to your backend deployment:
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION_NAME=far_documents`

## Post-Deployment

1. **Update CORS**: Add your frontend URL to `CORS_ORIGINS` in backend env vars
2. **Update API URL**: Set `REACT_APP_BACKEND_URL` in frontend to your backend URL
3. **Test the chatbot**: Verify queries work end-to-end
4. **Monitor logs**: Check Railway/Render logs for any errors

## Cost Estimates

### Free Tier (Good for personal use)
- Vercel/Netlify: Free
- Railway/Render: Free tier (limited hours)
- Supabase: Free tier (500MB)
- Qdrant Cloud: Check your current plan
- OpenAI API: Pay per use (~$0.10 per 1000 queries)

### Paid (Production ready)
- Vercel Pro: $20/month
- Railway: ~$5-10/month
- Supabase Pro: $25/month
- Total: ~$50-60/month

## Environment Variables Checklist

Backend:
- [ ] OPENAI_API_KEY
- [ ] QDRANT_URL
- [ ] QDRANT_API_KEY
- [ ] DATABASE_URL
- [ ] CORS_ORIGINS

Frontend:
- [ ] REACT_APP_BACKEND_URL

## Troubleshooting

**CORS errors**: Make sure your frontend URL is in `CORS_ORIGINS`
**API not responding**: Check backend logs and ensure PORT is not hardcoded
**Embeddings timeout**: Consider increasing request timeout in production

## Custom Domain (Optional)

Both Vercel and Netlify support custom domains:
1. Add your domain in the hosting platform
2. Update DNS records (they'll provide instructions)
3. SSL is automatically configured

## Need Help?

- Railway: https://docs.railway.app
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs
- Netlify: https://docs.netlify.com
