"""
Integration Tests for Chat Endpoint

Tests the complete chat API flow with real HTTP requests and mocked external services
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import status


class TestChatEndpointIntegration:
    """Integration tests for /api/v1/chat endpoint"""

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_chat_simple_query_success(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db,
        test_client
    ):
        """Test simple successful query through API"""
        # Mock context
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        # Mock LLM
        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT SUM(balance) as total FROM table',
            'explanation': 'Calculates total balance',
            'metrics_used': ['total_exposure']
        })
        mock_get_llm.return_value = mock_llm

        # Mock database
        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[{'total': 2800000000}])
        mock_get_db.return_value = mock_db

        # Make request
        response = test_client.post(
            "/api/v1/chat",
            json={"query": "What is the total exposure?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'result' in data
        assert data['result']['sql'] is not None
        assert len(data['result']['results']) > 0

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_chat_with_conversation_history(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db,
        test_client
    ):
        """Test chat with conversation history"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT 1',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[])
        mock_get_db.return_value = mock_db

        response = test_client.post(
            "/api/v1/chat",
            json={
                "query": "What about regions?",
                "conversation_history": [
                    {"role": "user", "content": "What is total exposure?"},
                    {"role": "assistant", "content": "$2.8B"}
                ]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_chat_ambiguous_query_returns_400(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db,
        test_client
    ):
        """Test that ambiguous query returns 400 with suggestions"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': True,
            'reasons': ['Missing time period'],
            'suggestions': ['Specify a time period']
        })
        mock_get_llm.return_value = mock_llm

        response = test_client.post(
            "/api/v1/chat",
            json={"query": "Show me the metrics"}
        )

        assert response.status_code == 400
        data = response.json()
        # Error details are nested under 'detail' key for HTTP exceptions
        assert 'detail' in data
        detail = data['detail']
        assert 'suggestions' in detail or 'reasons' in detail

    @pytest.mark.asyncio
    def test_chat_invalid_request_422(self, test_client):
        """Test that invalid request returns 422"""
        # Missing required 'query' field
        response = test_client.post(
            "/api/v1/chat",
            json={}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    def test_chat_query_too_long_422(self, test_client):
        """Test that query > 1000 chars returns 422"""
        long_query = "a" * 1001

        response = test_client.post(
            "/api/v1/chat",
            json={"query": long_query}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_chat_response_has_all_fields(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db,
        test_client
    ):
        """Test that response includes all required fields"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT 1',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[])
        mock_get_db.return_value = mock_db

        response = test_client.post(
            "/api/v1/chat",
            json={"query": "Test query"}
        )

        assert response.status_code == 200
        data = response.json()

        # Check all required fields
        assert 'success' in data
        assert 'query' in data
        assert 'conversation_id' in data
        assert 'result' in data
        assert 'timestamp' in data
        assert 'processing_time_ms' in data

        # Check result fields
        result = data['result']
        assert 'sql' in result
        assert 'explanation' in result
        assert 'results' in result
        assert 'metrics_used' in result
        assert 'visualization_hint' in result
        assert 'row_count' in result

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_chat_response_conversation_id(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db,
        test_client
    ):
        """Test that conversation ID is preserved"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT 1',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[])
        mock_get_db.return_value = mock_db

        response = test_client.post(
            "/api/v1/chat",
            json={
                "query": "Test query",
                "conversation_id": "test-conversation-123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['conversation_id'] == "test-conversation-123"

    @pytest.mark.asyncio
    async def test_chat_cors_headers(self, test_client):
        """Test that CORS headers are present"""
        response = test_client.post(
            "/api/v1/chat",
            json={"query": "Test"},
            headers={"Origin": "http://localhost:3000"}
        )

        # CORS headers should be present
        assert 'access-control-allow-origin' in [h.lower() for h in response.headers.keys()]

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_chat_check_ambiguity_false_skips_check(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db,
        test_client
    ):
        """Test that check_ambiguity=false skips ambiguity check"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        # Ambiguity check should NOT be called
        mock_llm.detect_ambiguity = AsyncMock()
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT 1',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[])
        mock_get_db.return_value = mock_db

        response = test_client.post(
            "/api/v1/chat",
            json={
                "query": "Test query",
                "check_ambiguity": False
            }
        )

        assert response.status_code == 200
        # Verify detect_ambiguity was not called
        mock_llm.detect_ambiguity.assert_not_called()
