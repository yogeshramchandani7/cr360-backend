# CR360 - Quick Start Guide

Get CR360 up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.10+ installed (`python --version`)
- [ ] Backend `.env` file configured with API keys
- [ ] Internet connection (for Gemini API and Supabase)

## 🚀 Option 1: Run Frontend Only (Testing)

If you just want to see the frontend UI:

```bash
cd cr360-frontend
npm install
npm run dev
```

Open http://localhost:5173

*Note: You'll get connection errors without backend running*

## 🚀 Option 2: Run Full Stack (Recommended)

### Step 1: Start Backend

Open **Terminal 1**:

```bash
# From project root (cr360_Backend/)
uvicorn app.main:app --reload
```

Wait for:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 2: Start Frontend

Open **Terminal 2**:

```bash
# From project root (cr360_Backend/)
cd cr360-frontend
npm run dev
```

Wait for:
```
  VITE v7.3.0  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

### Step 3: Open Browser

1. Navigate to: **http://localhost:5173**
2. Open DevTools (F12) → Console tab
3. You should see initialization logs

### Step 4: Try a Query

Type in the chat:
```
What is the total outstanding balance?
```

You should see:
1. Loading spinner
2. API logs in console
3. Results table with data
4. SQL query (click to expand)

## ✅ Verification Checklist

### Backend Health

Open: http://localhost:8000/health

Should see:
```json
{
  "status": "healthy",
  "components": {
    "database": "up",
    "context_loader": "up",
    "llm": "configured"
  }
}
```

### Frontend Health

Browser console should show:
```
[timestamp] [INFO] CR360 Frontend initialized
[timestamp] [INFO] API Client initialized {"baseUrl":"http://localhost:8000"}
```

### Full Integration

Try these queries in order:

1. **Simple Query:**
   ```
   What is the total outstanding balance?
   ```
   Expected: 1 row with total amount

2. **Ambiguous Query:**
   ```
   Show me delinquency
   ```
   Expected: Yellow ambiguity card with suggestions

3. **Breakdown Query:**
   ```
   Show me delinquency rates by product for Q4 2024
   ```
   Expected: Table with products and rates

## 🐛 Troubleshooting

### Backend won't start

**Error:** `ImportError: No module named 'fastapi'`

**Fix:**
```bash
pip install -r requirements.txt
```

**Error:** `ConfigurationError: Missing environment variable`

**Fix:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Frontend won't start

**Error:** `Cannot find module`

**Fix:**
```bash
cd cr360-frontend
npm install
```

**Error:** `Port 5173 already in use`

**Fix:**
```bash
lsof -ti:5173 | xargs kill -9
npm run dev
```

### Connection Errors

**Error in browser:** `Failed to fetch`

**Checklist:**
- [ ] Backend running on port 8000?
- [ ] Check `cr360-frontend/.env` has correct URL
- [ ] CORS enabled in backend `app/config.py`?

**Fix CORS:**

Edit `app/config.py`:
```python
CORS_ORIGINS = "http://localhost:5173,http://localhost:3000"
```

Restart backend.

### No Data / Empty Results

**Error:** `No results to display`

**Possible causes:**
1. Database not populated
2. SQL query returns no rows
3. Wrong table/date filter

**Check backend logs:**
```bash
# You should see SQL being executed
[INFO] SQL generated: SELECT ...
```

### Ambiguity Detection Not Working

If all queries return ambiguity:
- Check Gemini API key in `.env`
- Check backend logs for LLM errors
- Try: `check_ambiguity: false` in request

## 📊 Example Session

Here's what a successful session looks like:

### Terminal 1 (Backend)
```
INFO: Loading context from: context/cr360_semantic_model_v2.yaml
INFO: Context loaded successfully
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: chat_request_received query="What is the total outstanding balance?"
INFO: sql_generated sql="SELECT SUM(adjusted_eop_balance)..."
INFO: chat_request_completed processing_time_ms=1234
```

### Terminal 2 (Frontend)
```
VITE v7.3.0  ready in 543 ms
➜  Local:   http://localhost:5173/
```

### Browser Console
```
[2024-12-29T...] [INFO] CR360 Frontend initialized
[2024-12-29T...] [INFO] API Client initialized
[2024-12-29T...] [DEBUG] Component mounted: Chat
[2024-12-29T...] [INFO] User submitted query
[2024-12-29T...] [DEBUG] API Request {"method":"POST",...}
[2024-12-29T...] [DEBUG] API Response {"status":200,...}
[2024-12-29T...] [INFO] Query successful {"rowCount":1,...}
```

### Browser UI
```
┌─────────────────────────────────────────┐
│ CR360 Credit Risk Analytics             │
│ Ask questions in natural language...    │
├─────────────────────────────────────────┤
│                                          │
│ 👤 What is the total outstanding balance?│
│                                          │
│ 🤖 Found 1 results in 1234ms            │
│    ┌──────────────────────────────────┐ │
│    │ Explanation                       │ │
│    │ This shows the total outstanding │ │
│    │ balance across all accounts...   │ │
│    ├──────────────────────────────────┤ │
│    │ ▼ View SQL Query                 │ │
│    ├──────────────────────────────────┤ │
│    │ Results                          │ │
│    │ Sum                              │ │
│    │ 50,000,000.00                   │ │
│    │ Showing 1 row                    │ │
│    └──────────────────────────────────┘ │
│                                          │
│ [Type your question here...    ] [Send] │
└─────────────────────────────────────────┘
```

## 🎯 Next Steps

Once everything is working:

1. **Explore Features**
   - Try different query types
   - Click on ambiguity suggestions
   - Expand SQL queries
   - Check browser console logs

2. **Read Documentation**
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System overview
   - [cr360-frontend/README.md](cr360-frontend/README.md) - Frontend docs
   - [cr360-frontend/FEATURES.md](cr360-frontend/FEATURES.md) - Feature details

3. **Customize**
   - Add your own example queries
   - Modify styling (Tailwind CSS)
   - Add new components

4. **Deploy**
   - Build frontend: `npm run build`
   - Deploy to production server

## 📞 Support

If you're stuck:

1. Check logs in both terminals
2. Check browser console (F12)
3. Verify all prerequisites
4. Check [FRONTEND_SETUP.md](FRONTEND_SETUP.md)
5. Review error messages carefully

## 🎉 Success!

If you can:
- ✅ See the chat interface
- ✅ Submit a query
- ✅ Get results in a table
- ✅ See logs in browser console

**You're all set! Start querying your credit portfolio!** 🚀

---

**Time to Complete:** ~5 minutes
**Difficulty:** Easy
**Required Skills:** Basic terminal usage
