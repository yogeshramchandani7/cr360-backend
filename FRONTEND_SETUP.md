# CR360 Frontend Setup Guide

This guide will help you get the CR360 frontend up and running.

## Quick Start

### 1. Navigate to Frontend Directory

```bash
cd cr360-frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173**

## Running Frontend and Backend Together

### Terminal 1 - Start Backend

```bash
# From the project root (cr360_Backend/)
uvicorn app.main:app --reload
```

Backend will run on: **http://localhost:8000**

### Terminal 2 - Start Frontend

```bash
# From the project root (cr360_Backend/)
cd cr360-frontend
npm run dev
```

Frontend will run on: **http://localhost:5173**

## Testing the Application

1. Make sure both backend and frontend are running
2. Open http://localhost:5173 in your browser
3. Try these example queries:
   - "What is the total outstanding balance?"
   - "Show me delinquency rates by product"
   - "What is the ECL coverage ratio for Q4 2024?"

## Debugging

### Check Backend Connection

Open browser DevTools (F12) → Console tab. You should see:

```
[2024-12-29T...] [INFO] CR360 Frontend initialized
[2024-12-29T...] [INFO] API Client initialized {"baseUrl":"http://localhost:8000"}
```

If you see connection errors:
1. Verify backend is running (`uvicorn app.main:app --reload`)
2. Check the backend URL in `cr360-frontend/.env`
3. Ensure CORS is configured in backend

### View API Calls

All API requests and responses are logged to the browser console with full details:

- Request payload
- Response data
- Processing time
- Error details (if any)

## Project Structure

```
cr360-frontend/
├── src/
│   ├── components/       # React components
│   │   ├── Chat.tsx     # Main chat interface
│   │   ├── ResultsTable.tsx
│   │   ├── AmbiguityCard.tsx
│   │   ├── ErrorCard.tsx
│   │   └── LoadingSpinner.tsx
│   │
│   ├── services/
│   │   └── api.ts       # Backend API client
│   │
│   ├── types/
│   │   └── api.ts       # TypeScript types
│   │
│   ├── utils/
│   │   └── logger.ts    # Logging utility
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
│
├── .env                 # Environment configuration
├── package.json
└── README.md           # Detailed documentation
```

## Features Implemented

✅ Natural language query interface
✅ Real-time results with formatted tables
✅ Ambiguity detection with suggestions
✅ Conversation history (multi-turn)
✅ SQL query display
✅ Comprehensive logging
✅ Error handling
✅ Loading states
✅ Responsive design with Tailwind CSS

## Next Steps (Optional Enhancements)

- [ ] Add data visualization (charts using Recharts)
- [ ] Export results to CSV/Excel
- [ ] Dark mode toggle
- [ ] Query history sidebar
- [ ] User authentication
- [ ] Saved queries/bookmarks
- [ ] Advanced filters UI
- [ ] Mobile optimization

## Troubleshooting

### Build Errors

```bash
cd cr360-frontend
npm run build
```

If you see errors, check:
- TypeScript errors in the output
- Missing dependencies (`npm install`)

### Port Already in Use

If port 5173 is busy:

```bash
# Kill the process using the port
lsof -ti:5173 | xargs kill -9

# Or specify a different port
npm run dev -- --port 3000
```

### CORS Errors

If you see CORS errors in browser console, update backend CORS settings in `app/config.py`:

```python
CORS_ORIGINS = "http://localhost:5173,http://localhost:3000"
```

## Support

For detailed documentation, see:
- [Frontend README](cr360-frontend/README.md)
- [Backend README](README.md)

---

Happy querying! 🚀
