# Railway Deployment Guide - CR360

This guide walks you through deploying the CR360 application (backend + frontend) to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push your code to GitHub
3. **Environment Variables Ready**: Supabase credentials, Google API key

## Architecture Overview

We deploy two separate Railway services:
- **Backend Service**: FastAPI + Uvicorn (Python)
- **Frontend Service**: React + Nginx (Docker)

---

## Phase 1: Deploy Backend

### Step 1: Create New Project

1. Log in to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `cr360_Backend`
5. Railway will auto-detect the Dockerfile

### Step 2: Configure Backend Service

1. **Service Name**: Rename to `cr360-backend`
2. **Root Directory**: Leave as `/` (root of repo)
3. **Dockerfile Path**: Railway auto-detects `Dockerfile` at root

### Step 3: Set Environment Variables

Go to **Variables** tab and add:

```
# Application
APP_NAME=CR360
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# Supabase
SUPABASE_URL=https://ptlpjmhsmxejfaxniept.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB0bHBqbWhzbXhlamZheG5pZXB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU4NjU1NTgsImV4cCI6MjA4MTQ0MTU1OH0.ojhtkahuENh1Gp3kNaqWNljF-HTrpFTnLKapYQNNFxw
DATABASE_URL=postgresql://postgres:jeJ6aZkqPLL9FBsB@db.ptlpjmhsmxejfaxniept.supabase.co:5432/postgres

# Gemini API
GOOGLE_API_KEY=AIzaSyAxf7qRe8MlCQ6viBYdsRmiF_uHMJhqTCQ

# Context
CONTEXT_FILE_PATH=./context/semantic_model_prod.yaml

# LLM Settings
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=8192

# Memory
MAX_CONVERSATION_TURNS=5

# CORS - UPDATE AFTER FRONTEND DEPLOYMENT
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend.up.railway.app

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

**Important**: You'll update `CORS_ORIGINS` after deploying frontend.

### Step 4: Configure Port

1. Go to **Settings** tab
2. Under **Networking**, ensure port `8000` is exposed (should auto-detect from Dockerfile)

### Step 5: Deploy

1. Click **"Deploy"**
2. Watch build logs for any errors
3. Once deployed, note your backend URL: `https://your-backend.up.railway.app`

### Step 6: Test Backend

Test health endpoint:
```bash
curl https://your-backend.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-06T...",
  "components": {
    "database": "healthy",
    "context_loader": "healthy",
    "llm": "configured"
  }
}
```

---

## Phase 2: Deploy Frontend

### Step 1: Update .env.production

In `cr360-frontend/.env.production`, update with your backend URL:

```env
VITE_API_BASE_URL=https://your-backend.up.railway.app
```

Commit and push this change:
```bash
cd cr360-frontend
git add .env.production
git commit -m "Update production API URL"
git push
```

### Step 2: Create Frontend Service

1. In the same Railway project, click **"New Service"**
2. Select **"Deploy from GitHub repo"**
3. Choose the same repository
4. Railway will create a second service

### Step 3: Configure Frontend Service

1. **Service Name**: Rename to `cr360-frontend`
2. **Root Directory**: Set to `/cr360-frontend` (important!)
3. **Dockerfile Path**: `/cr360-frontend/Dockerfile`

### Step 4: Configure Port

1. Go to **Settings** tab
2. Under **Networking**, ensure port `80` is exposed (Nginx default)
3. Enable **"Generate Domain"** to get a Railway subdomain

### Step 5: Deploy

1. Click **"Deploy"**
2. Watch build logs:
   - Stage 1: Node.js build (npm ci, npm run build)
   - Stage 2: Nginx setup
3. Once deployed, note your frontend URL: `https://your-frontend.up.railway.app`

### Step 6: Test Frontend

1. Open `https://your-frontend.up.railway.app` in browser
2. Verify the CR360 chat interface loads
3. Test a sample query: "What is the total outstanding balance for Q4 2024?"

---

## Phase 3: Update CORS Configuration

Now that both services are deployed, update backend CORS:

### Step 1: Update Backend Environment Variable

1. Go to backend service in Railway
2. Navigate to **Variables** tab
3. Update `CORS_ORIGINS`:
```
CORS_ORIGINS=https://your-frontend.up.railway.app
```
4. Save - Railway will automatically redeploy

### Step 2: Verify CORS

Test from browser console on frontend:
```javascript
fetch('https://your-backend.up.railway.app/health')
  .then(r => r.json())
  .then(console.log)
```

Should succeed without CORS errors.

---

## Phase 4: Custom Domains (Optional)

### Option A: Railway Subdomains (Free)

Railway automatically provides subdomains:
- Backend: `cr360-backend.up.railway.app`
- Frontend: `cr360-frontend.up.railway.app`

These work immediately, no configuration needed.

### Option B: Custom Domain (Requires DNS Setup)

1. Go to service **Settings** > **Networking**
2. Click **"Add Custom Domain"**
3. Enter your domain (e.g., `app.cr360.com`)
4. Railway provides CNAME record: `your-service.up.railway.app`
5. Add CNAME in your DNS provider:
   - Name: `app` (or `@` for root)
   - Value: `your-service.up.railway.app`
6. Wait for DNS propagation (5-60 minutes)
7. Railway auto-provisions SSL certificate

**Example DNS Setup:**
```
Type    Name    Value
CNAME   app     cr360-frontend.up.railway.app
CNAME   api     cr360-backend.up.railway.app
```

**Important**: After adding custom domain, update:
1. Frontend `.env.production` with new backend URL
2. Backend `CORS_ORIGINS` with new frontend URL

---

## Phase 5: Monitoring & Logs

### View Logs

**Backend Logs:**
1. Select `cr360-backend` service
2. Click **"Logs"** tab
3. Filter by log level (INFO, ERROR, etc.)

**Frontend Logs:**
1. Select `cr360-frontend` service
2. Click **"Logs"** tab
3. Check Nginx access logs

### Monitor Metrics

Railway provides built-in metrics:
- **CPU Usage**: Click **"Metrics"** tab
- **Memory Usage**: Monitor for memory leaks
- **Network Traffic**: Bandwidth usage
- **Request Count**: HTTP requests/second

### Set Up Alerts (Optional)

1. Go to **Project Settings**
2. Configure **Webhooks** for deployment notifications
3. Integrate with Slack/Discord for real-time alerts

---

## Phase 6: Troubleshooting

### Backend Issues

**Issue**: Build fails with "requirements.txt not found"
- **Fix**: Ensure `requirements.txt` is at repo root
- Check `.dockerignore` doesn't exclude it

**Issue**: Health check returns 503
- **Fix**: Check logs for database connection errors
- Verify `DATABASE_URL` environment variable
- Ensure Supabase allows Railway IPs (usually auto-allowed)

**Issue**: "Context file not found" error
- **Fix**: Verify `context/semantic_model_prod.yaml` exists in repo
- Check `CONTEXT_FILE_PATH` environment variable

### Frontend Issues

**Issue**: Build fails with npm errors
- **Fix**: Clear Railway cache (Settings > Clear Build Cache)
- Ensure `package-lock.json` is committed

**Issue**: Frontend loads but shows "Network Error"
- **Fix**: Check `.env.production` has correct backend URL
- Verify backend CORS includes frontend URL
- Check browser console for exact error

**Issue**: 404 on refresh (SPA routing)
- **Fix**: Verify `nginx.conf` has `try_files $uri $uri/ /index.html;`
- Already configured in our setup

### General Issues

**Issue**: Slow response times
- **Fix**: Upgrade Railway plan for more resources
- Monitor metrics to identify bottleneck
- Consider Redis caching (future enhancement)

**Issue**: CORS errors
- **Fix**: Ensure `CORS_ORIGINS` in backend matches frontend URL exactly
- Include protocol (https://) and no trailing slash
- Redeploy backend after updating CORS

---

## Configuration Files Created

All deployment configuration files have been created:

### Backend Files
- ✅ `cr360_Backend/.dockerignore` - Optimizes Docker build
- ✅ `cr360_Backend/Dockerfile` - Already exists, Railway-ready

### Frontend Files
- ✅ `cr360-frontend/Dockerfile` - Multi-stage build (Node.js + Nginx)
- ✅ `cr360-frontend/nginx.conf` - Nginx web server config
- ✅ `cr360-frontend/.dockerignore` - Optimizes Docker build
- ✅ `cr360-frontend/.env.production` - Production API URL
- ✅ `cr360-frontend/vite.config.ts` - Updated with production optimizations

---

## Deployment Checklist

- [ ] Backend deployed to Railway
- [ ] Backend health check returns 200
- [ ] Frontend `.env.production` updated with backend URL
- [ ] Frontend deployed to Railway
- [ ] Frontend loads in browser
- [ ] Backend CORS updated with frontend URL
- [ ] Test query works end-to-end
- [ ] (Optional) Custom domains configured
- [ ] (Optional) Monitoring/alerts set up

---

## Quick Deploy Commands

### Option 1: Railway Dashboard (Recommended)
Follow the steps above in the Railway web interface.

### Option 2: Railway CLI (Advanced)

Install CLI:
```bash
npm install -g @railway/cli
railway login
```

Deploy backend:
```bash
cd cr360_Backend
railway init
railway up
railway variables set SUPABASE_URL=...
railway open
```

Deploy frontend:
```bash
cd cr360-frontend
railway init
railway up
railway open
```

---

## Cost Estimate

**Railway Pricing:**
- **Developer Plan**: $5/month/user
  - $5 usage included
  - Pay-as-you-go after
  - ~550 hours/month for small services

**Estimated Monthly Cost:**
- Small traffic: $5-15/month
- Medium traffic: $20-40/month
- Includes both backend + frontend

**Free Tier:**
- Trial plan available (limited hours)
- Good for testing deployment

---

## Next Steps

1. Deploy backend following Phase 1
2. Deploy frontend following Phase 2
3. Test end-to-end functionality
4. (Optional) Set up custom domains
5. Monitor logs for first 24 hours
6. Share URL with users!

**Your CR360 app will be live at:**
- Frontend: `https://your-frontend.up.railway.app`
- Backend API: `https://your-backend.up.railway.app`

---

## Support Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Vite Production Build**: https://vitejs.dev/guide/build.html

---

**Deployment Prepared**: 2026-01-06
**Configuration Files**: Ready ✅
**Ready to Deploy**: Yes! 🚀
