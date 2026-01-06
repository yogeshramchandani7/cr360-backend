"""
Shared Test Fixtures and Mocks for CR360 Backend Test Suite

This module provides centralized test fixtures used across all test files:
- Configuration mocks
- Database mocks
- LLM (Gemini) mocks
- Context loader mocks
- HTTP test client
- Sample data fixtures
"""

import pytest
import os
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi.testclient import TestClient


# ============================================================================
# Test Isolation - Singleton Reset
# ============================================================================

@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reset all singleton instances before each test to ensure test isolation.

    This fixture runs automatically before every test to prevent singleton
    instances from persisting between tests, which can cause mock contamination.
    """
    # Reset TextToSQLEngine singleton
    import app.query.text_to_sql as tts_module
    tts_module._text_to_sql_engine = None

    # Reset ContextLoader singleton
    import app.llm.context_loader as cl_module
    cl_module._context_loader = None

    # Reset DatabaseClient singleton
    import app.database.client as db_module
    db_module._database_client = None

    # Reset GeminiClient singleton
    import app.llm.gemini_client as gc_module
    gc_module._gemini_client = None

    yield

    # Clean up after test
    tts_module._text_to_sql_engine = None
    cl_module._context_loader = None
    db_module._database_client = None
    gc_module._gemini_client = None


# ============================================================================
# Configuration Mocks
# ============================================================================

@pytest.fixture
def mock_settings():
    """Mock Settings object with test configuration"""
    from app.config import Settings

    with patch('app.config.Settings') as mock:
        settings = Mock(spec=Settings)
        settings.APP_NAME = "CR360 Test"
        settings.APP_VERSION = "1.0.0-test"
        settings.ENVIRONMENT = "test"
        settings.LOG_LEVEL = "INFO"

        # Database settings
        settings.SUPABASE_URL = "https://test.supabase.co"
        settings.SUPABASE_KEY = "test_key_123"
        settings.DATABASE_URL = "postgresql://test:test@localhost:5432/test_db"

        # LLM settings
        settings.GOOGLE_API_KEY = "test_google_api_key"
        settings.LLM_MODEL = "gemini-2.5-flash-preview"
        settings.LLM_TEMPERATURE = 0.1
        settings.LLM_MAX_TOKENS = 8192

        # CORS settings
        settings.CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]

        # Context settings
        settings.CONTEXT_FILE_PATH = "context/cr360_semantic_model_v2.yaml"

        yield settings


@pytest.fixture
def test_env_vars(monkeypatch):
    """Set environment variables for testing"""
    env_vars = {
        "APP_NAME": "CR360 Test",
        "APP_VERSION": "1.0.0-test",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "INFO",
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test_key_123",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "GOOGLE_API_KEY": "test_google_api_key",
        "LLM_MODEL": "gemini-2.5-flash-preview",
        "LLM_TEMPERATURE": "0.1",
        "LLM_MAX_TOKENS": "8192",
        "CORS_ORIGINS": "http://localhost:3000,http://localhost:8000",
        "SEMANTIC_MODEL_PATH": "context/cr360_semantic_model_v2.yaml"
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    yield env_vars


# ============================================================================
# Database Mocks
# ============================================================================

@pytest.fixture
def sample_query_results():
    """Sample database query results (list of dicts)"""
    return [
        {
            "product_name": "Mortgage",
            "total_exposure": 1500000000.00,
            "delinquency_rate": 2.5,
            "charge_off_rate": 0.8
        },
        {
            "product_name": "Auto Loan",
            "total_exposure": 800000000.00,
            "delinquency_rate": 3.2,
            "charge_off_rate": 1.2
        },
        {
            "product_name": "Credit Card",
            "total_exposure": 500000000.00,
            "delinquency_rate": 4.1,
            "charge_off_rate": 2.1
        }
    ]


@pytest.fixture
def sample_empty_results():
    """Empty query results"""
    return []


@pytest.fixture
def mock_db_connection():
    """Mock psycopg2 connection and cursor"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = []
    mock_cursor.description = [
        ("product_name",),
        ("total_exposure",),
        ("delinquency_rate",),
        ("charge_off_rate",)
    ]

    mock_conn = Mock()
    mock_conn.cursor.return_value = mock_cursor

    yield mock_conn


@pytest.fixture
def mock_database_client(sample_query_results):
    """Mock DatabaseClient with sample responses"""
    from app.database.client import DatabaseClient

    mock_client = Mock(spec=DatabaseClient)

    # Mock execute_query as async
    async def mock_execute_query(sql: str):
        # Simulate different responses based on SQL content
        if "COUNT(*)" in sql.upper():
            return [{"count": 2109406}]
        elif "SUM(" in sql.upper() and "product_name" in sql.lower():
            return sample_query_results
        elif "WHERE" in sql.upper() and "date" in sql.lower():
            return sample_query_results[:1]
        else:
            return sample_query_results

    mock_client.execute_query = AsyncMock(side_effect=mock_execute_query)

    # Mock test_connection as async
    mock_client.test_connection = AsyncMock(return_value=True)

    # Mock close
    mock_client.close = Mock()

    yield mock_client


# ============================================================================
# LLM (Gemini) Mocks
# ============================================================================

@pytest.fixture
def sample_sql_response():
    """Sample LLM response with SQL, explanation, and metrics"""
    return """```sql
SELECT
    product_name,
    SUM(account_balance_eop) as total_exposure,
    (SUM(total_delinquent_balance) / NULLIF(SUM(account_balance_eop), 0)) * 100 as delinquency_rate,
    (SUM(charge_off_amount_ytd) / NULLIF(SUM(account_balance_boy), 0)) * 100 as charge_off_rate
FROM account_level_monthly
WHERE calendar_date = (SELECT MAX(calendar_date) FROM account_level_monthly)
GROUP BY product_name
ORDER BY product_name
```

Explanation: This query retrieves the total exposure, delinquency rate, and charge-off rate for each product using the latest available date. It aggregates account balances and calculates rates using NULLIF to avoid division by zero.

Metrics used: total_exposure, delinquency_rate, charge_off_rate
"""


@pytest.fixture
def sample_ambiguous_response():
    """Sample ambiguity detection response"""
    return """Ambiguous: Yes

Reasons:
- Missing time period specification
- Unclear aggregation level

Suggestions:
- Specify a time period (e.g., "as of latest date", "for Q4 2024")
- Specify aggregation level (e.g., "by product", "by region")
"""


@pytest.fixture
def sample_clear_response():
    """Sample response for clear (non-ambiguous) query"""
    return """{
  "is_ambiguous": false,
  "reasons": [],
  "suggestions": []
}"""


@pytest.fixture
def mock_gemini_api_response(sample_sql_response):
    """Mock google.generativeai response structure"""
    mock_response = Mock()
    mock_response.text = sample_sql_response
    mock_response.candidates = [Mock()]
    mock_response.prompt_feedback = Mock()

    yield mock_response


@pytest.fixture
def mock_gemini_client(sample_sql_response, sample_clear_response):
    """Mock GeminiClient with sample SQL responses"""
    from app.llm.gemini_client import GeminiClient

    mock_client = Mock(spec=GeminiClient)

    # Mock generate as async
    mock_client.generate = AsyncMock(return_value=sample_sql_response)

    # Mock generate_with_context as async
    mock_client.generate_with_context = AsyncMock(return_value=sample_sql_response)

    # Mock generate_sql as async
    async def mock_generate_sql(query, context, history=None):
        return {
            'sql': """SELECT
    SUM(account_balance_eop) as total_exposure
FROM account_level_monthly
WHERE calendar_date = (SELECT MAX(calendar_date) FROM account_level_monthly)""",
            'explanation': "This query retrieves the total exposure using the latest available date.",
            'metrics_used': ['total_exposure']
        }

    mock_client.generate_sql = AsyncMock(side_effect=mock_generate_sql)

    # Mock detect_ambiguity as async
    async def mock_detect_ambiguity(query, context):
        return {
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        }

    mock_client.detect_ambiguity = AsyncMock(side_effect=mock_detect_ambiguity)

    # Mock _parse_sql_response
    def mock_parse_sql_response(response):
        return (
            "SELECT SUM(account_balance_eop) FROM account_level_monthly",
            "Sample explanation",
            ['total_exposure']
        )

    mock_client._parse_sql_response = Mock(side_effect=mock_parse_sql_response)

    yield mock_client


# ============================================================================
# Context Loader Mocks
# ============================================================================

@pytest.fixture
def sample_semantic_context():
    """Minimal valid YAML semantic model for testing"""
    return """
version: "2.0"
metadata:
  name: "CR360 Test Semantic Model"
  description: "Test semantic model"
  last_updated: "2024-12-16"

data_model:
  primary_table: "account_level_monthly"
  date_column: "calendar_date"

dimensions:
  product:
    column: "product_name"
    levels: ["Mortgage", "Auto Loan", "Credit Card"]

  region:
    column: "region_name"
    levels: ["Northeast", "Southeast", "Midwest", "West", "Canada"]

  segment:
    column: "segment_name"
    levels: ["Prime", "Near-Prime", "Subprime"]

metrics:
  exposure:
    description: "Total account balance"
    metrics:
      - total_exposure
    calculation:
      formula: "SUM(account_balance_eop)"

  delinquency:
    description: "Delinquency metrics"
    metrics:
      - delinquency_rate
    calculation:
      formula: "(SUM(total_delinquent_balance) / NULLIF(SUM(account_balance_eop), 0)) * 100"
"""


@pytest.fixture
def mock_context_loader(sample_semantic_context):
    """Mock ContextLoader with test semantic model"""
    from app.llm.context_loader import ContextLoader

    mock_loader = Mock(spec=ContextLoader)

    # Mock get_context_for_llm
    mock_loader.get_context_for_llm = Mock(return_value=sample_semantic_context)

    # Mock get_metrics
    mock_loader.get_metrics = Mock(return_value=[
        'total_exposure',
        'delinquency_rate',
        'charge_off_rate',
        'net_charge_off_rate'
    ])

    # Mock get_dimensions
    mock_loader.get_dimensions = Mock(return_value=[
        'product_name',
        'region_name',
        'segment_name'
    ])

    # Mock context property
    mock_loader.context = {
        'version': '2.0',
        'metadata': {
            'name': 'CR360 Test Semantic Model',
            'description': 'Test semantic model'
        },
        'dimensions': {
            'product': {
                'column': 'product_name',
                'values': ['Mortgage', 'Auto Loan', 'Credit Card']
            }
        },
        'metrics': {
            'exposure': {
                'description': 'Total account balance',
                'metrics': ['total_exposure']
            }
        }
    }

    yield mock_loader


# ============================================================================
# HTTP Test Client
# ============================================================================

@pytest.fixture
def test_client():
    """FastAPI TestClient for endpoint testing"""
    from app.main import app

    client = TestClient(app)
    yield client


@pytest.fixture
def authorized_headers():
    """Mock authorization headers"""
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token_123"
    }


# ============================================================================
# Sample Request/Response Data
# ============================================================================

@pytest.fixture
def sample_chat_request():
    """Valid ChatRequest data"""
    return {
        "query": "What is the total exposure for Mortgage products?",
        "conversation_id": "test-conversation-123",
        "check_ambiguity": True,
        "session_id": "test-session-456"
    }


@pytest.fixture
def sample_chat_request_minimal():
    """Minimal valid ChatRequest data"""
    return {
        "query": "What is the total exposure?"
    }


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history (3 turns)"""
    return [
        {
            "role": "user",
            "content": "What is the total exposure?",
            "timestamp": "2024-12-16T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "The total exposure is $2.8B.",
            "timestamp": "2024-12-16T10:00:02Z"
        },
        {
            "role": "user",
            "content": "Show me by product",
            "timestamp": "2024-12-16T10:00:10Z"
        },
        {
            "role": "assistant",
            "content": "Here's the breakdown by product: Mortgage $1.5B, Auto Loan $800M, Credit Card $500M.",
            "timestamp": "2024-12-16T10:00:12Z"
        },
        {
            "role": "user",
            "content": "What about delinquency rates?",
            "timestamp": "2024-12-16T10:00:20Z"
        }
    ]


@pytest.fixture
def sample_query_result():
    """Sample QueryResult data"""
    return {
        "sql": "SELECT SUM(account_balance_eop) as total_exposure FROM account_level_monthly WHERE calendar_date = (SELECT MAX(calendar_date) FROM account_level_monthly)",
        "explanation": "This query retrieves the total exposure using the latest available date.",
        "results": [{"total_exposure": 2800000000.00}],
        "metrics_used": ["total_exposure"],
        "visualization_hint": "bar",
        "row_count": 1
    }


@pytest.fixture
def sample_chat_response(sample_query_result):
    """Sample ChatResponse data"""
    return {
        "success": True,
        "query": "What is the total exposure?",
        "conversation_id": "test-conversation-123",
        "result": sample_query_result,
        "error": None,
        "suggestions": None,
        "timestamp": datetime.utcnow().isoformat(),
        "processing_time_ms": 523.45
    }


@pytest.fixture
def sample_ambiguity_response():
    """Sample AmbiguityResponse data"""
    return {
        "success": False,
        "query": "Show me the metrics",
        "is_ambiguous": True,
        "reasons": [
            "Multiple possible metric interpretations",
            "Missing time period specification"
        ],
        "suggestions": [
            "Specify which metrics (e.g., exposure, delinquency rate, charge-off rate)",
            "Specify a time period (e.g., 'as of latest date', 'for Q4 2024')"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture
def sample_error_response():
    """Sample ErrorResponse data"""
    return {
        "success": False,
        "error": "Failed to generate SQL query",
        "error_type": "SQLGenerationError",
        "details": {
            "original_error": "Invalid metric name in query"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Text-to-SQL Engine Mocks
# ============================================================================

@pytest.fixture
def mock_text_to_sql_engine(sample_query_result):
    """Mock TextToSQLEngine with sample responses"""
    from app.query.text_to_sql import TextToSQLEngine

    mock_engine = Mock(spec=TextToSQLEngine)

    # Mock process_query as async
    async def mock_process_query(query, history=None, check_ambiguity=True):
        return {
            'sql': sample_query_result['sql'],
            'explanation': sample_query_result['explanation'],
            'results': sample_query_result['results'],
            'metrics_used': sample_query_result['metrics_used'],
            'visualization_hint': sample_query_result['visualization_hint']
        }

    mock_engine.process_query = AsyncMock(side_effect=mock_process_query)

    # Mock internal methods
    mock_engine._check_ambiguity = AsyncMock(return_value={
        'is_ambiguous': False,
        'reasons': [],
        'suggestions': []
    })

    mock_engine._generate_sql = AsyncMock(return_value={
        'sql': sample_query_result['sql'],
        'explanation': sample_query_result['explanation'],
        'metrics_used': sample_query_result['metrics_used']
    })

    mock_engine._validate_sql = Mock(return_value={
        'is_valid': True,
        'errors': []
    })

    mock_engine._execute_sql = AsyncMock(return_value=sample_query_result['results'])

    mock_engine._suggest_visualization = Mock(return_value='bar')

    yield mock_engine


# ============================================================================
# Patch Helpers
# ============================================================================

@pytest.fixture
def patch_get_gemini_client(mock_gemini_client):
    """Patch get_gemini_client() to return mock"""
    with patch('app.llm.gemini_client.get_gemini_client', return_value=mock_gemini_client):
        yield mock_gemini_client


@pytest.fixture
def patch_get_database_client(mock_database_client):
    """Patch get_database_client() to return mock"""
    with patch('app.database.client.get_database_client', return_value=mock_database_client):
        yield mock_database_client


@pytest.fixture
def patch_get_context_loader(mock_context_loader):
    """Patch get_context_loader() to return mock"""
    with patch('app.llm.context_loader.get_context_loader', return_value=mock_context_loader):
        yield mock_context_loader


@pytest.fixture
def patch_get_text_to_sql_engine(mock_text_to_sql_engine):
    """Patch get_text_to_sql_engine() to return mock"""
    with patch('app.query.text_to_sql.get_text_to_sql_engine', return_value=mock_text_to_sql_engine):
        yield mock_text_to_sql_engine


# ============================================================================
# Async Test Helpers
# ============================================================================

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
