# GitHub Pages Deployment Guide

## Architecture
- **Frontend**: GitHub Pages (FREE!) - `https://bashiraziz.github.io/far-reference-book/`
- **Backend**: Railway.app or Render.com (FREE tier available)

## Quick Deploy Steps

### Step 1: Enable GitHub Pages

1. Go to your repository: `https://github.com/bashiraziz/far-reference-book`
2. Click **Settings** → **Pages**
3. Under "Build and deployment":
   - Source: **GitHub Actions**
4. Done! GitHub Actions will deploy automatically

### Step 2: Deploy Backend to Railway (FREE)

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `bashiraziz/far-reference-book`
5. Railway will detect the `railway.json` config
6. Add environment variables:
   ```
   OPENAI_API_KEY=your_key_here
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_key
   DATABASE_URL=your_postgres_url
   CORS_ORIGINS=https://bashiraziz.github.io
   ```
7. Click "Deploy"
8. Copy the Railway URL (e.g., `https://your-app.up.railway.app`)

### Step 3: Update Frontend API URL

1. Edit `src/services/chatApi.ts`
2. Change line 8 to your Railway URL:
   ```typescript
   const API_BASE_URL = typeof window !== 'undefined' && (window as any).env?.REACT_APP_BACKEND_URL
     || 'https://your-app.up.railway.app';  // <-- Your Railway URL
   ```
3. Commit and push:
   ```bash
   git add .
   git commit -m "Update API URL for production"
   git push origin main
   ```

### Step 4: Test Your Site!

Your site will be live at:
- **Frontend**: https://bashiraziz.github.io/far-reference-book/
- **Backend**: https://your-app.up.railway.app

## Cost Breakdown

### FREE Tier (Perfect for personal use)
- ✅ GitHub Pages: **FREE** unlimited
- ✅ Railway: **FREE** ($5 credit/month, ~500 hours)
- ✅ Qdrant Cloud: Check your current plan
- 💰 OpenAI API: Pay-per-use (~$0.10 per 1000 queries)

**Total: $0-5/month** (depending on OpenAI usage)

### Paid (If you outgrow free tier)
- Railway Pro: $5/month base + usage
- Total: ~$10-20/month

## Database Setup (One-time)

You need a PostgreSQL database. **Recommended: Railway PostgreSQL (FREE)**

1. In Railway, click "New" → "Database" → "Add PostgreSQL"
2. Railway will create a database and provide a connection string
3. Copy the `DATABASE_URL` to your environment variables
4. Run migrations (first time only):
   ```bash
   # From your local machine
   export DATABASE_URL="your_railway_postgres_url"
   cd backend
   python -m alembic upgrade head
   ```

## Monitoring & Logs

- **Frontend builds**: Check "Actions" tab in GitHub
- **Backend logs**: Railway dashboard → Your service → "Logs"
- **Errors**: Railway will email you if deployment fails

## Troubleshooting

### Build fails on GitHub Actions
- Check the "Actions" tab for error logs
- Common issue: Missing dependencies → check `package.json`

### API not connecting
1. Check CORS settings in Railway env vars
2. Verify `CORS_ORIGINS=https://bashiraziz.github.io`
3. Check backend logs in Railway

### 404 errors on refresh
- This is normal for client-side routing
- GitHub Pages handles this automatically for Docusaurus

## Custom Domain (Optional)

Want `far-reference.com` instead of `bashiraziz.github.io`?

1. Buy domain (Namecheap, Google Domains, etc.)
2. GitHub Settings → Pages → Custom domain
3. Add DNS records (GitHub provides instructions)
4. Update `url` in `docusaurus.config.ts`

## Manual Deployment (if needed)

```bash
# Build locally
npm run build

# Deploy to gh-pages branch
npm run deploy
```

## Environment Variables Summary

### Backend (Railway)
```env
OPENAI_API_KEY=sk-...
QDRANT_URL=https://...
QDRANT_API_KEY=...
DATABASE_URL=postgresql://...
CORS_ORIGINS=https://bashiraziz.github.io
QDRANT_COLLECTION_NAME=far_documents
```

### Frontend
No environment variables needed! API URL is hardcoded in `chatApi.ts`

## Next Steps

1. ✅ Push your code to GitHub
2. ✅ Enable GitHub Pages in Settings
3. ✅ Deploy backend to Railway
4. ✅ Update API URL in code
5. ✅ Push again
6. 🎉 Your site is live!

## Support

- GitHub Pages: https://docs.github.com/en/pages
- Railway: https://docs.railway.app
- Docusaurus: https://docusaurus.io/docs/deployment
