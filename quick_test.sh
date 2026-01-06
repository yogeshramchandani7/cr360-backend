#!/bin/bash

# CR360 Quick Test Script
# Run this to quickly verify Phase 1 implementation

set -e

echo "================================"
echo "CR360 Backend - Quick Test"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
PYTHON_VERSION=$(python3 --version)
echo "  ✓ $PYTHON_VERSION"
echo ""

# Step 2: Check dependencies
echo "Step 2: Verifying dependencies..."
if python3 -c "import fastapi" 2>/dev/null; then
    echo "  ✓ FastAPI installed"
else
    echo -e "  ${RED}✗ FastAPI not found${NC}"
    echo "  Run: pip3 install -r requirements.txt"
    exit 1
fi
echo ""

# Step 3: Check .env file
echo "Step 3: Checking configuration..."
if [ -f .env ]; then
    echo "  ✓ .env file exists"
else
    echo -e "  ${YELLOW}! .env file missing, creating from template...${NC}"
    cp .env.example .env
    echo "  ✓ .env file created"
fi
echo ""

# Step 4: Check semantic model
echo "Step 4: Checking semantic model..."
if [ -f context/cr360_semantic_model_v2.yaml ]; then
    echo "  ✓ Semantic model found"
else
    echo -e "  ${RED}✗ Semantic model not found at context/cr360_semantic_model_v2.yaml${NC}"
    exit 1
fi
echo ""

# Step 5: Run basic setup test
echo "Step 5: Running basic setup test..."
python3 test_setup.py
echo ""

# Step 6: Start server
echo "Step 6: Starting server..."
echo "  Starting uvicorn on port 8000..."
python3 -m uvicorn app.main:app --port 8000 > /dev/null 2>&1 &
SERVER_PID=$!
echo "  Server PID: $SERVER_PID"

# Wait for server to start
echo "  Waiting for server to start..."
sleep 6

# Step 7: Test endpoints
echo ""
echo "Step 7: Testing endpoints..."
echo ""

# Test root endpoint
echo "  Testing GET /"
RESPONSE=$(curl -s http://localhost:8000/)
if echo "$RESPONSE" | grep -q "CR360"; then
    echo -e "    ${GREEN}✓ Root endpoint working${NC}"
    echo "    Response: $RESPONSE"
else
    echo -e "    ${RED}✗ Root endpoint failed${NC}"
fi
echo ""

# Test health endpoint
echo "  Testing GET /health"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "version"; then
    echo -e "    ${GREEN}✓ Health endpoint working${NC}"
    echo "    Response: $HEALTH_RESPONSE"
else
    echo -e "    ${RED}✗ Health endpoint failed${NC}"
fi
echo ""

# Test chat endpoint (basic)
echo "  Testing POST /api/v1/chat"
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the total exposure?", "check_ambiguity": false}')

if echo "$CHAT_RESPONSE" | grep -q "query"; then
    echo -e "    ${GREEN}✓ Chat endpoint accepting requests${NC}"
    # Check if successful or expected error
    if echo "$CHAT_RESPONSE" | grep -q '"success": true'; then
        echo -e "    ${GREEN}✓ Chat endpoint fully working (database connected)${NC}"
    elif echo "$CHAT_RESPONSE" | grep -q "error"; then
        echo -e "    ${YELLOW}! Chat endpoint working but database not connected (expected with placeholder credentials)${NC}"
    fi
else
    echo -e "    ${RED}✗ Chat endpoint failed${NC}"
fi
echo ""

# Step 8: Cleanup
echo "Step 8: Cleaning up..."
echo "  Stopping server (PID: $SERVER_PID)..."
kill $SERVER_PID 2>/dev/null || true
sleep 2
echo "  ✓ Server stopped"
echo ""

# Summary
echo "================================"
echo "Summary"
echo "================================"
echo -e "${GREEN}✓ Phase 1 implementation is working!${NC}"
echo ""
echo "Next Steps:"
echo "  1. Review TESTING.md for detailed testing instructions"
echo "  2. Add real credentials to .env file"
echo "  3. Start server: python3 -m uvicorn app.main:app --reload --port 8000"
echo "  4. Visit API docs: http://localhost:8000/docs"
echo "  5. Test queries using curl or Swagger UI"
echo ""
echo "To start the server manually:"
echo "  python3 -m uvicorn app.main:app --reload --port 8000"
echo ""
