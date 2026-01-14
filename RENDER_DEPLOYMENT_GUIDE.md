# Render.com Deployment Guide - CR360

## Why Render.com?

- ✅ **100% Free tier** (no credit card required)
- ✅ Auto-deploy from GitHub
- ✅ Supports Docker (both backend and frontend)
- ✅ PostgreSQL connections
- ✅ Custom domains
- ⚠️ Free tier has slower cold starts (services sleep after 15 min inactivity)

---

## Prerequisites

1. **Render Account**: Sign up at https://render.com (use GitHub login)
2. **GitHub Repository**: Already done ✅ (https://github.com/yogeshramchandani7/cr360-backend)
3. **Environment Variables**: Ready in .env file ✅

---

## Step 1: Deploy Backend Service

### 1.1 Create Backend Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub account (if not already connected)
4. Select repository: **`yogeshramchandani7/cr360-backend`**

### 1.2 Configure Backend Service

**Basic Settings:**
- **Name**: `cr360-backend`
- **Region**: `Oregon (US West)` or closest to you
- **Branch**: `main`
- **Root Directory**: `.` (leave empty or use `.`)
- **Runtime**: `Docker`
- **Dockerfile Path**: `Dockerfile` (auto-detected)

**Instance Type:**
- **Free** (select this!)

**Advanced Settings:**

1. Click **"Advanced"**

2. **Environment Variables** - Add these:

```
APP_NAME=CR360
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

SUPABASE_URL=https://ptlpjmhsmxejfaxniept.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB0bHBqbWhzbXhlamZheG5pZXB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU4NjU1NTgsImV4cCI6MjA4MTQ0MTU1OH0.ojhtkahuENh1Gp3kNaqWNljF-HTrpFTnLKapYQNNFxw
DATABASE_URL=postgresql://postgres:jeJ6aZkqPLL9FBsB@db.ptlpjmhsmxejfaxniept.supabase.co:5432/postgres

GOOGLE_API_KEY=AIzaSyAxf7qRe8MlCQ6viBYdsRmiF_uHMJhqTCQ

CONTEXT_FILE_PATH=./context/semantic_model_prod.yaml

LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=8192

MAX_CONVERSATION_TURNS=5

CORS_ORIGINS=http://localhost:3000,http://localhost:5173

RATE_LIMIT_PER_MINUTE=60
```

3. **Auto-Deploy**: `Yes` (enabled by default)

4. Click **"Create Web Service"**

### 1.3 Wait for Deployment

- Watch build logs in Render dashboard
- Build takes ~3-5 minutes
- Status will show "Live" when ready
- Your backend URL: `https://cr360-backend.onrender.com`

### 1.4 Test Backend

```bash
curl https://cr360-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "components": {
    "database": "healthy",
    "context_loader": "healthy",
    "llm": "configured"
  }
}
```

---

## Step 2: Deploy Frontend Service

### 2.1 Update Frontend Environment Variable

First, update frontend .env.production with backend URL:

```bash
# This will be done automatically by script
```

### 2.2 Create Frontend Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Select repository: **`yogeshramchandani7/cr360-backend`**

### 2.3 Configure Frontend Service

**Basic Settings:**
- **Name**: `cr360-frontend`
- **Region**: `Oregon (US West)` (same as backend)
- **Branch**: `main`
- **Root Directory**: `cr360-frontend`
- **Runtime**: `Docker`
- **Dockerfile Path**: `cr360-frontend/Dockerfile`

**Instance Type:**
- **Free**

**Advanced Settings:**

1. Click **"Advanced"**

2. **Environment Variables** - Add:

```
VITE_API_BASE_URL=https://cr360-backend.onrender.com
```

3. **Auto-Deploy**: `Yes`

4. Click **"Create Web Service"**

### 2.4 Wait for Deployment

- Build takes ~5-7 minutes (Node.js + Nginx)
- Status will show "Live" when ready
- Your frontend URL: `https://cr360-frontend.onrender.com`

---

## Step 3: Update Backend CORS

### 3.1 Add Frontend URL to CORS

1. Go to backend service in Render dashboard
2. Click **"Environment"** tab
3. Find `CORS_ORIGINS` variable
4. Update to:

```
CORS_ORIGINS=https://cr360-frontend.onrender.com
```

5. Click **"Save Changes"**
6. Render will auto-redeploy backend (takes ~2 minutes)

---

## Step 4: Test End-to-End

1. Open frontend: `https://cr360-frontend.onrender.com`
2. Type a query: `"What is the total outstanding balance for Q4 2024?"`
3. Verify results display correctly

---

## Important Notes

### Free Tier Limitations

⚠️ **Services sleep after 15 minutes of inactivity**
- First request after sleep: 30-60 second cold start
- Subsequent requests: Normal speed
- **Workaround**: Use a free uptime monitor (see below)

⚠️ **Build minutes limit**
- Free tier: 750 hours/month (plenty for small apps)
- Shared CPU (slower than paid tiers)

### Keep Services Awake (Optional)

Use a free uptime monitor to ping your services every 10 minutes:

**UptimeRobot** (https://uptimerobot.com):
1. Create free account
2. Add monitor for: `https://cr360-backend.onrender.com/health`
3. Check interval: 5 minutes
4. This keeps backend awake during business hours

---

## Render vs Railway Comparison

| Feature | Render (Free) | Railway (Trial) |
|---------|---------------|-----------------|
| **Cost** | Free forever | $5/month required |
| **Credit Card** | Not required | Required |
| **Cold Starts** | Yes (15 min) | No |
| **Build Time** | 3-7 min | 2-5 min |
| **Auto-Deploy** | ✅ Yes | ✅ Yes |
| **Custom Domains** | ✅ Yes | ✅ Yes |
| **PostgreSQL** | ✅ Yes | ✅ Yes |

---

## Deployment Checklist

- [ ] Backend deployed on Render
- [ ] Backend health check returns 200
- [ ] Frontend .env.production updated with backend URL
- [ ] Frontend deployed on Render
- [ ] Backend CORS updated with frontend URL
- [ ] Test query works end-to-end
- [ ] (Optional) Set up uptime monitor

---

## Troubleshooting

### Backend build fails

**Issue**: `requirements.txt not found`
- **Fix**: Ensure Root Directory is `.` (empty or dot)

### Frontend build fails

**Issue**: `npm install` errors
- **Fix**: Ensure Root Directory is `cr360-frontend`
- Check Dockerfile Path is `cr360-frontend/Dockerfile`

### CORS errors in browser

**Issue**: Frontend can't reach backend
- **Fix**: Verify `CORS_ORIGINS` in backend includes frontend URL
- Redeploy backend after changing CORS

### Slow first request (cold start)

**Issue**: 30-60 second delay after inactivity
- **Expected**: Free tier services sleep after 15 min
- **Fix**: Use UptimeRobot to keep awake, or upgrade to paid tier

---

## Next Steps

1. Deploy backend following Step 1
2. Note backend URL: `https://cr360-backend.onrender.com`
3. Deploy frontend following Step 2
4. Update CORS following Step 3
5. Test and share with users!

---

**Deployment Prepared**: 2026-01-06
**Platform**: Render.com (Free Tier)
**Estimated Cost**: $0/month 💰
