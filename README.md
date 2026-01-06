# CR360 Backend - GenAI-Powered Credit Risk Analytics

FastAPI backend for CR360 platform with Text-to-SQL generation, conversation memory, and progressive investigation capabilities.

## Features

- 🤖 **Text-to-SQL Generation** - Convert natural language to PostgreSQL queries using Gemini 2.5 Flash
- 💬 **Conversation Memory** - Multi-turn conversations with context preservation
- 🔍 **Investigation Agent** - Progressive root cause analysis with hypothesis generation
- 📊 **Automatic Visualization** - Intelligent chart selection and data formatting
- 🛡️ **Reliability Layer** - SQL validation, smart retry, and ambiguity detection

## Tech Stack

- **Framework:** FastAPI 0.104.1
- **LLM:** Google Gemini 2.5 Flash
- **Database:** Supabase (PostgreSQL)
- **Logging:** Structlog
- **Testing:** Pytest

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Supabase account with CR360 database setup
- Google Gemini API key

### 2. Installation

```bash
# Clone repository
git clone <repo-url>
cd cr360_Backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - SUPABASE_URL
# - SUPABASE_KEY
# - DATABASE_URL
# - GOOGLE_API_KEY
```

### 4. Run Locally

```bash
# Start the server
uvicorn app.main:app --reload --port 8000

# Test
curl http://localhost:8000
```

### 5. Run with Docker

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Stop
docker-compose down
```

## Project Structure

```
cr360_Backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── api/                 # API routes & schemas
│   ├── core/                # Orchestrator & business logic
│   ├── agents/              # Specialized AI agents
│   ├── llm/                 # LLM integration
│   ├── query/               # Text-to-SQL engine
│   ├── memory/              # Conversation memory
│   ├── reliability/         # SQL validation & retry
│   ├── investigation/       # Investigation agent
│   ├── visualization/       # Chart selection
│   ├── database/            # Database layer
│   └── utils/               # Logging & exceptions
├── context/                 # YAML semantic model
├── tests/                   # Test suite
└── scripts/                 # Utility scripts
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check (coming soon)
- `POST /api/v1/chat` - Chat endpoint (coming soon)

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Format code
black app/
ruff check app/

# Type checking
mypy app/
```

## Testing

### Quick Test (Automated)

Run the quick test script to verify everything is working:

```bash
./quick_test.sh
```

### Manual Testing

See [TESTING.md](TESTING.md) for comprehensive testing instructions including:
- Environment setup
- Endpoint testing
- Query examples
- Troubleshooting guide

### API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Implementation Status

**Phase 1: Foundation** ✅ **COMPLETE**
- [x] Project structure
- [x] Configuration & logging
- [x] FastAPI application
- [x] Docker setup
- [x] Context loader
- [x] LLM integration
- [x] Text-to-SQL engine
- [x] API endpoints

**Phase 2: Reliability & Memory (Next)**
- [ ] SQL validation
- [ ] Smart retry logic
- [ ] Conversation memory
- [ ] Ambiguity detection

**Phase 3: Investigation Agent**
- [ ] Hypothesis generation
- [ ] Multi-query execution
- [ ] Insight synthesis

**Phase 4: Visualization & Polish**
- [ ] Automatic chart selection
- [ ] Full orchestrator
- [ ] Golden test suite

## Documentation

- [Testing Guide](TESTING.md) ⭐ **Start here for testing**
- [Architecture Document](cr360_genai_architecture.md)
- [Semantic Model](context/cr360_semantic_model_v2.yaml)

## License

Proprietary - TD Bank

## Support

For issues or questions, contact the development team.
