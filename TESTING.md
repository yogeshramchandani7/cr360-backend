# CR360 Backend - Testing Guide

Complete step-by-step guide to test the Phase 1 implementation.

---

## Prerequisites

Before testing, ensure you have:

- [x] Python 3.11+ installed
- [x] All dependencies installed (`pip install -r requirements.txt`)
- [x] `.env` file created (copy from `.env.example`)

---

## Step 1: Verify Installation

Run the basic setup test:

```bash
python3 test_setup.py
```

**Expected Output:**
```
✅ Configuration loaded successfully
✅ Logging configured successfully
✅ FastAPI application created successfully
🎉 All basic setup tests passed!
```

**If this fails:** Install dependencies with `pip3 install -r requirements.txt`

---

## Step 2: Configure Environment Variables

### Option A: Test with Placeholder Credentials (Quick Test)

The `.env` file already has placeholder values. This will work for basic testing but database queries will fail.

```bash
# .env file already exists with placeholders
cat .env
```

### Option B: Add Real Credentials (Full Testing)

Edit `.env` file and add your actual credentials:

```bash
# Open .env in your editor
nano .env  # or code .env or vim .env
```

Update these values:

```bash
# Supabase - Get from https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=your_actual_supabase_anon_key_here

# Database - Get from Supabase Settings > Database > Connection String
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres

# Google Gemini API - Get from https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

Save and close the file.

---

## Step 3: Start the Application

### Method 1: Direct Start (Recommended for Testing)

```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
{"event": "Starting CR360 Backend", "level": "info", ...}
{"event": "loading_context", "level": "info", ...}
{"event": "context_loaded_successfully", "level": "info", "metrics_count": 12, ...}
{"event": "Loaded semantic model", "level": "info", ...}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Success Indicators:**
- ✅ `context_loaded_successfully` appears
- ✅ `Application startup complete` appears
- ✅ No error messages

**Common Errors:**
- ❌ `Context file not found` → Check that `context/cr360_semantic_model_v2.yaml` exists
- ❌ `ModuleNotFoundError` → Run `pip3 install -r requirements.txt`

### Method 2: Using Docker

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Stop
docker-compose down
```

---

## Step 4: Test the Endpoints

Keep the server running in one terminal, open a new terminal for testing.

### Test 1: Root Endpoint

```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "message": "Welcome to CR360",
  "version": "1.0.0",
  "status": "running"
}
```

### Test 2: Health Check Endpoint

```bash
curl http://localhost:8000/health
```

**Expected Response (with placeholder credentials):**
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2025-12-15T20:00:00.000000",
  "components": {
    "database": "unhealthy",
    "context_loader": "healthy",
    "llm": "configured"
  }
}
```

**Expected Response (with real credentials):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-15T20:00:00.000000",
  "components": {
    "database": "healthy",
    "context_loader": "healthy",
    "llm": "configured"
  }
}
```

### Test 3: Chat Endpoint (Basic Test)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the total exposure for Auto loans?",
    "check_ambiguity": false
  }'
```

**What This Tests:**
- API endpoint is working
- Request validation
- Query processing pipeline

**Expected Response (with real credentials):**
```json
{
  "success": true,
  "query": "What is the total exposure for Auto loans?",
  "conversation_id": "abc-123-def",
  "result": {
    "sql": "SELECT SUM(exposure) FROM ...",
    "explanation": "This query calculates...",
    "results": [...],
    "metrics_used": ["gross_credit_exposure"],
    "visualization_hint": "bar",
    "row_count": 5
  },
  "processing_time_ms": 1234.56
}
```

**Expected Response (with placeholder credentials - will fail):**
```json
{
  "success": false,
  "error": "Failed to execute query...",
  "error_type": "SQLExecutionError"
}
```

### Test 4: Ambiguity Detection

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the numbers",
    "check_ambiguity": true
  }'
```

**Expected Response:**
```json
{
  "success": false,
  "query": "Show me the numbers",
  "is_ambiguous": true,
  "reasons": [
    "Multiple possible metric interpretations",
    "Missing time period"
  ],
  "suggestions": [
    "Specify which metric (exposure, NCO, delinquency, etc.)",
    "Specify time period (last month, YTD, etc.)"
  ]
}
```

### Test 5: Conversation History

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What about for the Southeast region?",
    "conversation_id": "test-conversation-1",
    "conversation_history": [
      {
        "role": "user",
        "content": "What is the total exposure for Auto loans?"
      },
      {
        "role": "assistant",
        "content": "The total exposure is $5M"
      }
    ],
    "check_ambiguity": false
  }'
```

**What This Tests:**
- Conversation context preservation
- Multi-turn conversations

---

## Step 5: Interactive API Testing (Swagger UI)

FastAPI provides an interactive API documentation interface:

1. **Open in Browser:**
   ```
   http://localhost:8000/docs
   ```

2. **You'll see:**
   - List of all endpoints
   - Interactive "Try it out" buttons
   - Request/response schemas

3. **To Test an Endpoint:**
   - Click on an endpoint (e.g., `POST /api/v1/chat`)
   - Click "Try it out"
   - Edit the request body
   - Click "Execute"
   - See the response

**Alternative UI (ReDoc):**
```
http://localhost:8000/redoc
```

---

## Step 6: Test with Python Script

Create a test script to easily run multiple queries:

```bash
# Create test file
cat > test_chat.py << 'EOF'
import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat(query, check_ambiguity=True):
    """Test the chat endpoint"""
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        json={
            "query": query,
            "check_ambiguity": check_ambiguity
        }
    )
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

# Test queries
if __name__ == "__main__":
    # Test 1: Clear query
    test_chat("What is the total exposure for Auto loans?", check_ambiguity=False)

    # Test 2: Ambiguous query
    test_chat("Show me the numbers", check_ambiguity=True)

    # Test 3: Time-based query
    test_chat("What is the NCO rate trend for the last 6 months?", check_ambiguity=False)
EOF

# Run the test
python3 test_chat.py
```

---

## Step 7: Verify Logs

Check the application logs for detailed information:

### Console Logs

The application outputs structured JSON logs:

```json
{"event": "chat_request_received", "query": "...", "level": "info"}
{"event": "generating_sql_from_nl", "level": "info"}
{"event": "sql_generated", "sql_length": 150, "level": "info"}
{"event": "executing_sql", "level": "info"}
{"event": "chat_request_completed", "rows_returned": 5, "level": "info"}
```

### Log Levels

- `INFO` - Normal operations
- `WARNING` - Ambiguous queries, retries
- `ERROR` - Failures, exceptions

---

## Step 8: Common Test Scenarios

### Scenario 1: Basic Metric Query

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the gross credit exposure?", "check_ambiguity": false}'
```

### Scenario 2: Aggregation by Dimension

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me NCO rates by product", "check_ambiguity": false}'
```

### Scenario 3: Time Series Query

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me monthly delinquency rates for the last 6 months", "check_ambiguity": false}'
```

### Scenario 4: Filtered Query

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the exposure for Auto loans in the Southeast region?", "check_ambiguity": false}'
```

### Scenario 5: Comparison Query

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare NCO rates between Prime and Subprime segments", "check_ambiguity": false}'
```

---

## Step 9: Performance Testing

### Test Response Times

```bash
# Install httpie for better formatting (optional)
pip install httpie

# Make 10 requests and measure time
for i in {1..10}; do
  time curl -X POST http://localhost:8000/api/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "What is the total exposure?", "check_ambiguity": false}' \
    -s -o /dev/null
done
```

### Load Testing (Optional)

```bash
# Install locust for load testing
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class CR360User(HttpUser):
    wait_time = between(1, 3)

    @task
    def chat_query(self):
        self.client.post("/api/v1/chat", json={
            "query": "What is the total exposure?",
            "check_ambiguity": False
        })
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000
# Visit http://localhost:8089 to configure and start test
```

---

## Step 10: Troubleshooting

### Issue: "Context file not found"

**Solution:**
```bash
# Check if file exists
ls -la context/cr360_semantic_model_v2.yaml

# If missing, check if it's in root directory
ls -la cr360_semantic_model_v2.yaml

# Move to context directory
mkdir -p context
mv cr360_semantic_model_v2.yaml context/
```

### Issue: "Module not found"

**Solution:**
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
```

### Issue: "Database unhealthy"

**Solution:**
```bash
# Update .env with real credentials
nano .env

# Test database connection separately
python3 -c "
from app.database.client import get_database_client
import asyncio
async def test():
    client = get_database_client()
    result = await client.test_connection()
    print('Database connection:', 'OK' if result else 'FAILED')
asyncio.run(test())
"
```

### Issue: "LLM generation failed"

**Solution:**
```bash
# Verify Gemini API key
echo $GOOGLE_API_KEY  # or check .env file

# Test Gemini API separately
python3 -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content('Hello')
print('Gemini API:', 'OK' if response.text else 'FAILED')
print('Response:', response.text[:100])
"
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
python3 -m uvicorn app.main:app --port 8001
```

---

## Step 11: Automated Testing (Future)

Once you're ready to add automated tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_chat.py

# Run specific test
pytest tests/test_chat.py::test_basic_query
```

---

## Success Checklist

After completing all tests, you should have:

- [x] Application starts without errors
- [x] Root endpoint returns welcome message
- [x] Health check shows context_loader as "healthy"
- [x] Chat endpoint accepts requests (returns 200 or 400)
- [x] Swagger UI accessible at `/docs`
- [x] Logs show structured JSON output
- [x] No unhandled exceptions in console

---

## Quick Reference

### Start Server
```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

### Test Root
```bash
curl http://localhost:8000/
```

### Test Health
```bash
curl http://localhost:8000/health
```

### Test Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the total exposure?", "check_ambiguity": false}'
```

### View API Docs
```
http://localhost:8000/docs
```

### Stop Server
```bash
# If running in foreground: Ctrl+C
# If running in background:
pkill -f "uvicorn app.main:app"
```

---

## Next Steps After Testing

Once testing is complete:

1. ✅ Phase 1 validated
2. → Add real database credentials
3. → Test with actual Supabase data
4. → Implement Phase 2 (Reliability & Memory)
5. → Write automated tests
6. → Deploy to production

---

## Support

If you encounter issues:

1. Check the logs in the console
2. Verify `.env` file configuration
3. Ensure all dependencies are installed
4. Check this TESTING.md file for solutions

---

**Happy Testing! 🚀**
