#!/bin/bash
# Railway Deployment Script for CR360
# Run each section step-by-step

set -e  # Exit on error

echo "================================================"
echo "CR360 Railway Deployment Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Login to Railway
echo -e "${YELLOW}Step 1: Login to Railway${NC}"
echo "Run this command in your terminal:"
echo -e "${GREEN}railway login${NC}"
echo ""
echo "This will open your browser. Authenticate and come back."
echo "Press Enter when done..."
read -p ""

# Step 2: Create new project and deploy backend
echo ""
echo -e "${YELLOW}Step 2: Deploy Backend Service${NC}"
echo "Creating new Railway project and deploying backend..."
echo ""

# Initialize Railway project in backend directory
railway init --name cr360-backend

# Deploy backend
echo "Deploying backend..."
railway up

# Get the backend domain
echo ""
echo "Getting backend URL..."
BACKEND_URL=$(railway domain)
echo -e "${GREEN}Backend deployed at: $BACKEND_URL${NC}"
echo ""

# Step 3: Update frontend environment with backend URL
echo -e "${YELLOW}Step 3: Update Frontend Environment${NC}"
echo "Updating cr360-frontend/.env.production with backend URL..."

cat > cr360-frontend/.env.production << EOF
# Production Environment Variables
# Backend API URL (automatically updated by deployment script)
VITE_API_BASE_URL=https://$BACKEND_URL
EOF

echo -e "${GREEN}Updated .env.production with backend URL${NC}"
echo ""

# Step 4: Commit the updated .env.production
echo -e "${YELLOW}Step 4: Commit Frontend Environment Update${NC}"
git add cr360-frontend/.env.production
git commit -m "Update frontend .env.production with Railway backend URL"
echo -e "${GREEN}Committed frontend environment update${NC}"
echo ""

# Step 5: Deploy frontend as a separate service
echo -e "${YELLOW}Step 5: Deploy Frontend Service${NC}"
echo "Creating frontend service in the same project..."
echo ""

# We need to create a second service for frontend
# Railway CLI doesn't support multiple services in one command easily
# So we'll use the web dashboard approach

echo -e "${RED}IMPORTANT: Frontend deployment requires web dashboard${NC}"
echo ""
echo "Follow these steps in the Railway dashboard:"
echo "1. Go to https://railway.app/dashboard"
echo "2. Open your 'cr360-backend' project"
echo "3. Click 'New Service' button"
echo "4. Select 'GitHub Repo'"
echo "5. Choose the same repository"
echo "6. Configure the service:"
echo "   - Name: cr360-frontend"
echo "   - Root Directory: /cr360-frontend"
echo "   - Dockerfile Path: /cr360-frontend/Dockerfile"
echo "7. Click 'Deploy'"
echo ""
echo "Press Enter when frontend is deployed..."
read -p ""

# Step 6: Get frontend URL
echo ""
echo -e "${YELLOW}Step 6: Get Frontend URL${NC}"
echo "What is your frontend Railway URL?"
echo "(e.g., https://cr360-frontend-production-xxxx.up.railway.app)"
read -p "Frontend URL: " FRONTEND_URL

# Step 7: Update backend CORS
echo ""
echo -e "${YELLOW}Step 7: Update Backend CORS${NC}"
echo "Updating backend CORS to include frontend URL..."
echo ""
echo "In Railway dashboard:"
echo "1. Go to cr360-backend service"
echo "2. Click 'Variables' tab"
echo "3. Update CORS_ORIGINS to:"
echo -e "${GREEN}$FRONTEND_URL${NC}"
echo "4. Save (Railway will auto-redeploy)"
echo ""
echo "Press Enter when done..."
read -p ""

# Step 8: Summary
echo ""
echo "================================================"
echo -e "${GREEN}Deployment Complete!${NC}"
echo "================================================"
echo ""
echo -e "Backend URL:  ${GREEN}https://$BACKEND_URL${NC}"
echo -e "Frontend URL: ${GREEN}$FRONTEND_URL${NC}"
echo ""
echo "Next steps:"
echo "1. Test backend health: curl https://$BACKEND_URL/health"
echo "2. Open frontend: $FRONTEND_URL"
echo "3. Test a query: 'What is the total outstanding balance for Q4 2024?'"
echo ""
echo "Monitor logs:"
echo "- Backend:  railway logs --service cr360-backend"
echo "- Frontend: Check Railway dashboard"
echo ""
