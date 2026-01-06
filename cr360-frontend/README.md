# CR360 Credit Risk Analytics - Frontend

A minimalistic React-based frontend for the CR360 Credit Risk Analytics platform. This application provides a natural language chat interface for querying credit risk data.

## Features

- **Natural Language Queries** - Ask questions about credit portfolio in plain English
- **Real-time Results** - Instant query execution with formatted table display
- **Ambiguity Detection** - Intelligent query clarification with suggestions
- **Conversation History** - Multi-turn conversations with context preservation
- **Comprehensive Logging** - Full request/response logging for debugging
- **Error Handling** - User-friendly error messages and recovery
- **Responsive Design** - Clean, minimal UI with Tailwind CSS

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Comprehensive logging** for debugging

## Prerequisites

- Node.js 18+ and npm
- CR360 Backend running on `http://localhost:8000` (or configured URL)

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set your backend URL:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Project Structure

```
src/
├── components/          # React components
│   ├── Chat.tsx        # Main chat interface
│   ├── ResultsTable.tsx    # Data table display
│   ├── AmbiguityCard.tsx   # Ambiguity handling
│   ├── ErrorCard.tsx       # Error display
│   └── LoadingSpinner.tsx  # Loading indicator
│
├── services/           # API integration
│   └── api.ts         # Backend API client
│
├── types/             # TypeScript types
│   └── api.ts        # API request/response types
│
├── utils/            # Utilities
│   └── logger.ts    # Comprehensive logging
│
├── App.tsx          # Root component
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## Usage

### Example Queries

Try asking questions like:

- "What is the total outstanding balance?"
- "Show me delinquency rates by product"
- "What is the ECL coverage ratio for Q4 2024?"
- "Compare charge-off rates across regions"
- "Show accounts with days past due greater than 90"

### Features Walkthrough

#### 1. Chat Interface
- Type your question in natural language
- Click "Send" or press Enter
- View results in formatted tables

#### 2. Ambiguity Handling
- If your query is unclear, the system will ask for clarification
- Click on suggested queries to auto-fill them
- Refine your question and resubmit

#### 3. Conversation History
- Previous questions and answers are displayed in the chat
- Context is preserved across multiple questions
- Conversation ID is maintained for related queries

#### 4. SQL Display
- Click "View SQL Query" to see the generated SQL
- SQL is syntax-highlighted for readability
- Copy SQL for use in other tools

## Logging & Debugging

The frontend includes comprehensive logging to help debug issues:

### Browser Console Logs

Open browser DevTools (F12) and check the Console tab. You'll see:

- **API Requests** - Full request details (method, URL, payload)
- **API Responses** - Response status, data, and timing
- **Component Lifecycle** - Mount/unmount events
- **State Changes** - Track state updates
- **Errors** - Detailed error information with stack traces

### Log Format

```
[2024-12-29T12:34:56.789Z] [INFO] API Request {"method":"POST","url":"http://localhost:8000/api/v1/chat",...}
[2024-12-29T12:34:57.123Z] [INFO] Query successful {"conversationId":"abc-123","rowCount":5,...}
```

### Log Levels

- **DEBUG** - Detailed information (dev only)
- **INFO** - General information
- **WARN** - Warnings (non-critical issues)
- **ERROR** - Errors with full context

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## API Integration

The frontend communicates with the CR360 backend via REST API:

### Endpoints Used

- `GET /health` - Health check
- `POST /api/v1/chat` - Send queries and get results

### Request Format

```json
{
  "query": "What is the total outstanding balance?",
  "conversation_id": "optional-uuid",
  "conversation_history": [
    {"role": "user", "content": "previous question"},
    {"role": "assistant", "content": "previous answer"}
  ],
  "check_ambiguity": true
}
```

### Response Format

**Success:**
```json
{
  "success": true,
  "query": "...",
  "conversation_id": "...",
  "result": {
    "sql": "SELECT ...",
    "explanation": "...",
    "results": [{...}],
    "visualization_hint": "table",
    "row_count": 5
  },
  "processing_time_ms": 1234
}
```

**Ambiguous:**
```json
{
  "success": false,
  "error_type": "AmbiguousQueryError",
  "message": "Query needs clarification",
  "details": {
    "ambiguity_reasons": ["Missing time period"],
    "suggestions": ["What is the total outstanding balance as of Q4 2024?"]
  }
}
```

## Troubleshooting

### Cannot connect to backend

1. Ensure the backend is running (`uvicorn app.main:app --reload`)
2. Check `.env` file has correct `VITE_API_BASE_URL`
3. Verify CORS is configured on backend (check backend's `app/config.py`)

### No results displayed

1. Open browser DevTools (F12) → Console tab
2. Look for API errors or response issues
3. Check the backend logs for SQL errors

### Ambiguity errors

- Add more details to your query (time periods, filters, etc.)
- Click on suggested queries
- Be specific about what you're asking for

### TypeScript errors

```bash
npm run build
```

Will show any type errors that need fixing.

## Development

### Code Style

- TypeScript strict mode enabled
- Functional components with hooks
- Comprehensive logging on all operations
- Error boundaries for resilience

### Adding New Features

1. Create component in `src/components/`
2. Add types to `src/types/api.ts` if needed
3. Use logger for debugging: `logger.info('Message', context)`
4. Follow existing patterns (loading states, error handling)

## License

Proprietary - CR360 Project

## Support

For issues or questions, check:
1. Browser console logs
2. Backend logs
3. Network tab in DevTools

---

Built with React + TypeScript + Vite + Tailwind CSS
