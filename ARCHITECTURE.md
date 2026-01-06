# CR360 Full Stack Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                     http://localhost:5173                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REACT FRONTEND                              │
│                  (cr360-frontend/)                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Components                                               │  │
│  │  ├─ Chat.tsx           (Main interface)                  │  │
│  │  ├─ ResultsTable.tsx   (Data display)                    │  │
│  │  ├─ AmbiguityCard.tsx  (Clarifications)                  │  │
│  │  └─ ErrorCard.tsx      (Error handling)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Client (services/api.ts)                            │  │
│  │  - sendQuery()                                            │  │
│  │  - Comprehensive logging                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Logger (utils/logger.ts)                                │  │
│  │  - All operations logged to browser console              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ POST /api/v1/chat
                              │ GET /health
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│                    (cr360_Backend/app/)                          │
│                  http://localhost:8000                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Routes                                               │  │
│  │  ├─ POST /api/v1/chat  (Main query endpoint)            │  │
│  │  └─ GET /health        (Health check)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Text-to-SQL Engine (query/text_to_sql.py)              │  │
│  │  1. Ambiguity detection                                  │  │
│  │  2. SQL generation (via Gemini LLM)                     │  │
│  │  3. SQL validation                                       │  │
│  │  4. Query execution                                      │  │
│  │  5. Visualization hint                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Gemini LLM Client (llm/gemini_client.py)               │  │
│  │  - Natural language → SQL conversion                     │  │
│  │  - Two-tier routing logic                               │  │
│  │  - Context-aware generation                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                 │                            │                   │
│                 ▼                            ▼                   │
│  ┌──────────────────────┐    ┌─────────────────────────────┐  │
│  │  Context Loader       │    │  Database Client            │  │
│  │  (Semantic Model)     │    │  (PostgreSQL via Supabase)  │  │
│  │  - Metrics            │    │  - Execute SQL              │  │
│  │  - Dimensions         │    │  - Return results           │  │
│  │  - Business rules     │    └─────────────────────────────┘  │
│  └──────────────────────┘                  │                   │
└─────────────────────────────────────────────│───────────────────┘
                                              │
                                              ▼
                              ┌───────────────────────────────┐
                              │   SUPABASE (PostgreSQL)       │
                              │                               │
                              │  Tables:                      │
                              │  ├─ accounts (1,141 rows)    │
                              │  │   Account-level data      │
                              │  │                            │
                              │  └─ computed_metrics (8 rows) │
                              │      Portfolio aggregates    │
                              └───────────────────────────────┘
                                              │
                                              ▼
                              ┌───────────────────────────────┐
                              │   GOOGLE GEMINI API           │
                              │   (gemini-2.5-flash)         │
                              │                               │
                              │   - Natural language parsing  │
                              │   - SQL generation            │
                              │   - Ambiguity detection       │
                              └───────────────────────────────┘
```

## Data Flow: User Query to Results

```
1. USER TYPES QUERY
   "What is the total outstanding balance?"
   │
   ▼
2. FRONTEND (Chat.tsx)
   - Creates message object
   - Calls apiClient.sendQueryWithHistory()
   - Shows loading spinner
   │
   ▼
3. API CLIENT (services/api.ts)
   - Logs request details
   - Sends POST to /api/v1/chat
   - Includes conversation history
   │
   ▼
4. BACKEND API ROUTE (api/routes/chat.py)
   - Receives request
   - Validates input
   - Calls text_to_sql processor
   │
   ▼
5. TEXT-TO-SQL ENGINE (query/text_to_sql.py)
   ├─ Step 1: Check ambiguity
   │  └─ Gemini: "Is this query clear?"
   │
   ├─ Step 2: Generate SQL
   │  └─ Gemini: "Convert to SQL using semantic model"
   │     Result: "SELECT SUM(adjusted_eop_balance) FROM computed_metrics"
   │
   ├─ Step 3: Validate SQL
   │  └─ Check for dangerous keywords
   │
   ├─ Step 4: Execute SQL
   │  └─ Database: Run query
   │     Result: [{"sum": 50000000}]
   │
   └─ Step 5: Suggest visualization
      └─ "table" (simple aggregate)
   │
   ▼
6. BACKEND RESPONSE
   {
     "success": true,
     "result": {
       "sql": "SELECT ...",
       "explanation": "Shows total balance...",
       "results": [{"sum": 50000000}],
       "row_count": 1,
       "visualization_hint": "table"
     },
     "processing_time_ms": 1234
   }
   │
   ▼
7. FRONTEND (Chat.tsx)
   - Receives response
   - Logs to console
   - Renders ResultsTable component
   │
   ▼
8. RESULTS DISPLAYED
   ┌─────────────────────────┐
   │ Explanation             │
   │ Shows total balance... │
   ├─────────────────────────┤
   │ SQL (collapsible)      │
   │ SELECT SUM(...)        │
   ├─────────────────────────┤
   │ Results Table          │
   │ ┌──────────────────┐   │
   │ │ Sum              │   │
   │ ├──────────────────┤   │
   │ │ 50,000,000.00   │   │
   │ └──────────────────┘   │
   │ Showing 1 row          │
   └─────────────────────────┘
```

## Technology Stack Summary

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Custom Logger** - Debugging

### Backend
- **FastAPI** - Web framework
- **Google Gemini 2.5 Flash** - LLM for text-to-SQL
- **psycopg2** - PostgreSQL driver
- **Supabase** - Database hosting
- **Structlog** - Structured logging
- **Pydantic** - Data validation

### Database
- **PostgreSQL** - Relational database
- **Two-tier architecture**:
  - `accounts` - Granular data (1,141 rows)
  - `computed_metrics` - Pre-aggregated (8 rows)

## Key Features

### Frontend Features
✅ Chat-based interface
✅ Real-time query results
✅ Ambiguity handling with suggestions
✅ Multi-turn conversations
✅ SQL display with syntax highlighting
✅ Comprehensive browser logging
✅ Error handling with details
✅ Loading states
✅ Responsive design

### Backend Features
✅ Natural language to SQL conversion
✅ Two-tier database routing
✅ Query ambiguity detection
✅ SQL validation and safety checks
✅ Conversation memory
✅ Semantic model with 40+ metrics
✅ Visualization recommendations
✅ Structured JSON logging
✅ Health monitoring

## API Contract

### Request (POST /api/v1/chat)
```typescript
{
  query: string
  conversation_id?: string
  conversation_history?: Array<{role, content}>
  check_ambiguity?: boolean
}
```

### Response Types

**Success:**
```typescript
{
  success: true
  result: {
    sql: string
    explanation: string
    results: Array<Record<string, any>>
    metrics_used: string[]
    visualization_hint: string
    row_count: number
  }
  processing_time_ms: number
}
```

**Ambiguous:**
```typescript
{
  success: false
  error_type: "AmbiguousQueryError"
  details: {
    ambiguity_reasons: string[]
    suggestions: string[]
  }
}
```

**Error:**
```typescript
{
  success: false
  error_type: string
  message: string
  details?: any
}
```

## Logging & Observability

### Frontend Logging
- All API calls logged to browser console
- Component lifecycle events
- State changes tracked
- Errors with full context
- Format: `[timestamp] [level] message {context}`

### Backend Logging
- Structured JSON logs (production)
- Query processing pipeline tracked
- SQL generation and execution logged
- Error traces with context
- Performance metrics (processing time)

## Security

- ✅ SQL injection prevention (validation layer)
- ✅ Dangerous keyword blocking (DROP, DELETE, etc.)
- ✅ Environment-based configuration
- ✅ CORS configuration
- ✅ API key management
- ⚠️ Authentication (not yet implemented)
- ⚠️ Rate limiting (configured but basic)

## Performance

- **Frontend:** Vite hot reload (<100ms)
- **Backend:** Typical query processing: 1-3 seconds
  - Ambiguity check: ~500ms
  - SQL generation: ~800ms
  - SQL execution: ~200ms
  - Visualization: ~50ms
- **Database:** Pre-aggregated metrics for fast queries

---

**Last Updated:** 2024-12-29
