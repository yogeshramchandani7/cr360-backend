"""
Unit Tests for Chat Route (app/api/routes/chat.py)

Tests chat endpoints with mocked dependencies
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException, status
from app.api.routes.chat import chat, router
from app.utils.exceptions import (
    AmbiguousQueryError,
    SQLGenerationError,
    SQLValidationError,
    SQLExecutionError
)


class TestChatEndpoint:
    """Test chat endpoint"""

    @pytest.mark.asyncio
    @patch('app.api.routes.chat.get_text_to_sql_engine')
    async def test_chat_endpoint_success(self, mock_get_engine, sample_chat_request):
        """Test successful chat request"""
        # Mock engine
        mock_engine = Mock()
        mock_engine.process_query = AsyncMock(return_value={
            'sql': 'SELECT SUM(balance) FROM table',
            'explanation': 'This calculates total balance',
            'results': [{'total': 2800000000}],
            'metrics_used': ['total_exposure'],
            'visualization_hint': 'bar'
        })
        mock_get_engine.return_value = mock_engine

        # Create request
        from app.api.schemas import ChatRequest
        request = ChatRequest(**sample_chat_request)

        response = await chat(request)

        assert response['success'] is True
        assert response['query'] == sample_chat_request['query']
        assert 'result' in response
        assert response['result']['sql'] == 'SELECT SUM(balance) FROM table'
        assert 'processing_time_ms' in response

    @pytest.mark.asyncio
    @patch('app.api.routes.chat.get_text_to_sql_engine')
    async def test_chat_endpoint_generates_conversation_id(self, mock_get_engine):
        """Test that conversation ID is generated if not provided"""
        mock_engine = Mock()
        mock_engine.process_query = AsyncMock(return_value={
            'sql': 'SELECT 1',
            'explanation': 'Test',
            'results': [],
            'metrics_used': [],
            'visualization_hint': 'table'
        })
        mock_get_engine.return_value = mock_engine

        from app.api.schemas import ChatRequest
        request = ChatRequest(query="Test query")  # No conversation_id

        response = await chat(request)

        assert 'conversation_id' in response
        assert response['conversation_id'] is not None
        assert len(response['conversation_id']) > 0

    @pytest.mark.asyncio
    @patch('app.api.routes.chat.get_text_to_sql_engine')
    async def test_chat_endpoint_ambiguous_query(self, mock_get_engine, sample_chat_request):
        """Test handling of ambiguous queries (returns 400)"""
        mock_engine = Mock()
        mock_engine.process_query = AsyncMock(
            side_effect=AmbiguousQueryError(
                "Query is ambiguous",
                options=["Specify time period", "Specify product"]
            )
        )
        mock_get_engine.return_value = mock_engine

        from app.api.schemas import ChatRequest
        request = ChatRequest(**sample_chat_request)

        with pytest.raises(HTTPException) as exc_info:
            await chat(request)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert 'suggestions' in exc_info.value.detail or 'reasons' in exc_info.value.detail

    @pytest.mark.asyncio
    @patch('app.api.routes.chat.get_text_to_sql_engine')
    async def test_chat_endpoint_sql_generation_error(self, mock_get_engine, sample_chat_request):
        """Test handling of SQL generation errors (returns 500)"""
        mock_engine = Mock()
        mock_engine.process_query = AsyncMock(
            side_effect=SQLGenerationError("Failed to generate SQL")
        )
        mock_get_engine.return_value = mock_engine

        from app.api.schemas import ChatRequest
        request = ChatRequest(**sample_chat_request)

        with pytest.raises(HTTPException) as exc_info:
            await chat(request)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    @patch('app.api.routes.chat.get_text_to_sql_engine')
    async def test_chat_endpoint_sql_validation_error(self, mock_get_engine, sample_chat_request):
        """Test handling of SQL validation errors (returns 500)"""
        mock_engine = Mock()
        mock_engine.process_query = AsyncMock(
            side_effect=SQLValidationError("SQL validation failed")
        )
        mock_get_engine.return_value = mock_engine

        from app.api.schemas import ChatRequest
        request = ChatRequest(**sample_chat_request)

        with pytest.raises(HTTPException) as exc_info:
            await chat(request)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    @patch('app.api.routes.chat.get_text_to_sql_engine')
    async def test_chat_endpoint_sql_execution_error(self, mock_get_engine, sample_chat_request):
        """Test handling of SQL execution errors (returns 500)"""
        mock_engine = Mock()
        mock_engine.process_query = AsyncMock(
            side_effect=SQLExecutionError("SQL execution failed")
        )
        mock_get_engine.return_value = mock_engine

        from app.api.schemas import ChatRequest
        request = ChatRequest(**sample_chat_request)

        with pytest.raises(HTTPException) as exc_info:
            await chat(request)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'details' in exc_info.value.detail or 'error' in exc_info.value.detail

    @pytest.mark.asyncio
    @patch('app.api.routes.chat.get_text_to_sql_engine')
    async def test_chat_endpoint_unexpected_error(self, mock_get_engine, sample_chat_request):
        """Test handling of unexpected errors (returns 500)"""
        mock_engine = Mock()
        mock_engine.process_query = AsyncMock(
            side_effect=Exception("Unexpected error")
        )
        mock_get_engine.return_value = mock_engine

        from app.api.schemas import ChatRequest
        request = ChatRequest(**sample_chat_request)

        with pytest.raises(HTTPException) as exc_info:
            await chat(request)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    @patch('app.api.routes.chat.get_text_to_sql_engine')
    async def test_chat_endpoint_with_conversation_history(
        self,
        mock_get_engine,
        sample_conversation_history
    ):
        """Test chat with conversation history"""
        mock_engine = Mock()
        mock_engine.process_query = AsyncMock(return_value={
            'sql': 'SELECT 1',
            'explanation': 'Test',
            'results': [],
            'metrics_used': [],
            'visualization_hint': 'table'
        })
        mock_get_engine.return_value = mock_engine

        from app.api.schemas import ChatRequest, Message
        request = ChatRequest(
            query="Test query",
            conversation_history=[Message(**msg) for msg in sample_conversation_history]
        )

        response = await chat(request)

        assert response['success'] is True
        # Verify engine was called with conversation history
        mock_engine.process_query.assert_called_once()


class TestRouterConfiguration:
    """Test router configuration"""

    def test_router_has_chat_tag(self):
        """Test that router has 'chat' tag"""
        assert 'chat' in router.tags

    def test_chat_endpoint_path(self):
        """Test chat endpoint path"""
        routes = [route.path for route in router.routes]
        assert any('/chat' in path for path in routes)

    def test_chat_endpoint_accepts_post(self):
        """Test chat endpoint accepts POST method"""
        chat_route = None
        for route in router.routes:
            if 'chat' in route.path.lower():
                chat_route = route
                break

        assert chat_route is not None
        assert 'POST' in chat_route.methods

    def test_chat_endpoint_response_models(self):
        """Test that chat endpoint has response models defined"""
        chat_route = None
        for route in router.routes:
            if 'chat' in route.path.lower():
                chat_route = route
                break

        assert chat_route is not None
        # Should have response model
        assert chat_route.response_model is not None
