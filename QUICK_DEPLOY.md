# 🚀 Quick Deploy to GitHub Pages (5 Minutes!)

## Your Site Will Be:
- **Frontend**: https://bashiraziz.github.io/far-reference-book/ (FREE!)
- **Backend**: Railway.app (FREE tier - $5 credit/month)

## Step 1: Push to GitHub (2 minutes)

```bash
# Add all changes
git add .

# Commit
git commit -m "Add deployment configs and chatbot fixes"

# Push to GitHub
git push origin main
```

## Step 2: Enable GitHub Pages (1 minute)

1. Go to: https://github.com/bashiraziz/far-reference-book/settings/pages
2. Under "Build and deployment":
   - Source: Select **"GitHub Actions"**
3. Done! GitHub will automatically build and deploy

Wait 2-3 minutes, then check: https://bashiraziz.github.io/far-reference-book/

## Step 3: Deploy Backend to Railway (2 minutes)

### 3a. Sign up & Deploy
1. Go to: https://railway.app
2. Click "Login" → "Login with GitHub"
3. Click "New Project" → "Deploy from GitHub repo"
4. Select: `bashiraziz/far-reference-book`
5. Railway will auto-detect the config and start building

### 3b. Add Environment Variables
In Railway dashboard, click "Variables" tab and add:

```env
OPENAI_API_KEY=your_openai_key_here
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=far_documents
CORS_ORIGINS=https://bashiraziz.github.io
```

For database, click "+ New" → "Database" → "Add PostgreSQL"
Railway will automatically add `DATABASE_URL`

### 3c. Get Your Railway URL
After deployment, copy your Railway URL (e.g., `https://far-reference-book-production.up.railway.app`)

## Step 4: Update API URL (1 minute)

1. Edit `src/services/chatApi.ts` line 8
2. Change to your Railway URL:
```typescript
const API_BASE_URL = typeof window !== 'undefined' && (window as any).env?.REACT_APP_BACKEND_URL
  || 'https://your-app.up.railway.app';  // <-- Paste your Railway URL here
```

3. Commit and push:
```bash
git add src/services/chatApi.ts
git commit -m "Update production API URL"
git push origin main
```

GitHub Actions will rebuild automatically (takes 2-3 minutes)

## Step 5: Test! 🎉

Visit: https://bashiraziz.github.io/far-reference-book/

Try asking the chatbot:
- "What is FAR section 2.101?"
- "Tell me about gratuities"
- "Explain kickbacks in FAR Part 3"

## Troubleshooting

### Frontend not loading?
- Check GitHub Actions: https://github.com/bashiraziz/far-reference-book/actions
- If build failed, check the error logs

### Chatbot not responding?
1. Check Railway logs for errors
2. Verify CORS_ORIGINS includes: `https://bashiraziz.github.io`
3. Make sure all environment variables are set

### Database connection error?
1. In Railway, add PostgreSQL database
2. Run migrations once:
```bash
# Set the DATABASE_URL from Railway
export DATABASE_URL="postgresql://..."
cd backend
python -m alembic upgrade head
```

## Cost Summary

✅ **FREE Tier**:
- GitHub Pages: FREE (unlimited)
- Railway: FREE ($5/month credit = ~500 hours)
- OpenAI: Pay-per-use (~$0.10/1000 queries)

**Total: ~$0-5/month** depending on usage

## What's Next?

### Optional Improvements:
1. **Custom domain**: Buy domain → Point to GitHub Pages
2. **Monitoring**: Set up Railway alerts
3. **Analytics**: Add Google Analytics to Docusaurus

### Scaling Up:
When you outgrow free tier:
- Railway Pro: $5/month base + usage
- Upgrade Qdrant if needed
- Total: ~$10-20/month

## Need Help?

- **GitHub Actions failing**: Check the "Actions" tab
- **Railway issues**: Check Railway dashboard → Logs
- **API errors**: Check browser console (F12)

Full documentation: `GITHUB_PAGES_DEPLOY.md`
