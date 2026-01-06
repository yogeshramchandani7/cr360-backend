"""
Unit Tests for API Schemas (app/api/schemas/chat.py)

Tests Pydantic model validation, serialization, and edge cases
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from app.api.schemas import (
    Message,
    ChatRequest,
    QueryResult,
    ChatResponse,
    AmbiguityResponse,
    ErrorResponse,
    HealthResponse
)


class TestMessage:
    """Test Message schema"""

    def test_message_user_role_valid(self):
        """Test Message with user role"""
        msg = Message(
            role="user",
            content="What is the total exposure?"
        )

        assert msg.role == "user"
        assert msg.content == "What is the total exposure?"
        assert msg.timestamp is None  # Optional field

    def test_message_assistant_role_valid(self):
        """Test Message with assistant role"""
        msg = Message(
            role="assistant",
            content="The total exposure is $2.8B."
        )

        assert msg.role == "assistant"
        assert msg.content == "The total exposure is $2.8B."

    def test_message_with_timestamp(self):
        """Test Message with timestamp"""
        now = datetime.utcnow()
        msg = Message(
            role="user",
            content="Test message",
            timestamp=now
        )

        assert msg.timestamp == now

    def test_message_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing"""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user")  # Missing content

        error_str = str(exc_info.value)
        assert "content" in error_str


class TestChatRequest:
    """Test ChatRequest schema"""

    def test_chat_request_valid_complete(self, sample_conversation_history):
        """Test ChatRequest with all fields"""
        request = ChatRequest(
            query="What is the total exposure for Mortgage products?",
            conversation_id="test-conv-123",
            conversation_history=[
                Message(**msg) for msg in sample_conversation_history
            ],
            check_ambiguity=True,
            session_id="test-session-456"
        )

        assert request.query == "What is the total exposure for Mortgage products?"
        assert request.conversation_id == "test-conv-123"
        assert len(request.conversation_history) == 5
        assert request.check_ambiguity is True
        assert request.session_id == "test-session-456"

    def test_chat_request_minimal_valid(self):
        """Test ChatRequest with only required fields"""
        request = ChatRequest(query="What is the total exposure?")

        assert request.query == "What is the total exposure?"
        assert request.conversation_id is None
        assert request.conversation_history is None
        assert request.check_ambiguity is True  # Default value
        assert request.session_id is None

    def test_chat_request_query_too_short(self):
        """Test that query < 1 char is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(query="")

        error_str = str(exc_info.value)
        assert "query" in error_str

    def test_chat_request_query_too_long(self):
        """Test that query > 1000 chars is rejected"""
        long_query = "a" * 1001

        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(query=long_query)

        error_str = str(exc_info.value)
        assert "query" in error_str

    def test_chat_request_query_max_length_valid(self):
        """Test that query with exactly 1000 chars is valid"""
        max_query = "a" * 1000
        request = ChatRequest(query=max_query)

        assert len(request.query) == 1000

    def test_chat_request_check_ambiguity_default(self):
        """Test that check_ambiguity defaults to True"""
        request = ChatRequest(query="Test query")

        assert request.check_ambiguity is True

    def test_chat_request_check_ambiguity_false(self):
        """Test setting check_ambiguity to False"""
        request = ChatRequest(
            query="Test query",
            check_ambiguity=False
        )

        assert request.check_ambiguity is False

    def test_chat_request_missing_required_query(self):
        """Test that ValidationError is raised when query is missing"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest()

        error_str = str(exc_info.value)
        assert "query" in error_str


class TestQueryResult:
    """Test QueryResult schema"""

    def test_query_result_valid_complete(self, sample_query_results):
        """Test QueryResult with all fields"""
        result = QueryResult(
            sql="SELECT * FROM account_level_monthly",
            explanation="This query retrieves all account data",
            results=sample_query_results,
            metrics_used=["total_exposure", "delinquency_rate"],
            visualization_hint="bar",
            row_count=len(sample_query_results)
        )

        assert result.sql == "SELECT * FROM account_level_monthly"
        assert result.explanation == "This query retrieves all account data"
        assert len(result.results) == 3
        assert result.metrics_used == ["total_exposure", "delinquency_rate"]
        assert result.visualization_hint == "bar"
        assert result.row_count == 3

    def test_query_result_empty_results(self):
        """Test QueryResult with empty results list"""
        result = QueryResult(
            sql="SELECT * FROM table WHERE 1=0",
            explanation="Empty result set",
            results=[],
            metrics_used=[],
            visualization_hint="table",
            row_count=0
        )

        assert result.results == []
        assert result.row_count == 0

    def test_query_result_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing"""
        with pytest.raises(ValidationError) as exc_info:
            QueryResult(
                sql="SELECT * FROM table",
                # Missing other required fields
            )

        error_str = str(exc_info.value)
        assert "explanation" in error_str or "results" in error_str


class TestChatResponse:
    """Test ChatResponse schema"""

    def test_chat_response_success_complete(self, sample_query_result):
        """Test successful ChatResponse with all fields"""
        response = ChatResponse(
            success=True,
            query="What is the total exposure?",
            conversation_id="test-conv-123",
            result=QueryResult(**sample_query_result),
            processing_time_ms=523.45
        )

        assert response.success is True
        assert response.query == "What is the total exposure?"
        assert response.conversation_id == "test-conv-123"
        assert response.result is not None
        assert response.result.sql == sample_query_result['sql']
        assert response.error is None
        assert response.suggestions is None
        assert response.processing_time_ms == 523.45
        assert isinstance(response.timestamp, datetime)

    def test_chat_response_with_timestamp(self):
        """Test that ChatResponse includes timestamp"""
        response = ChatResponse(
            success=True,
            query="Test",
            conversation_id="test-123",
            result=None
        )

        assert isinstance(response.timestamp, datetime)
        # Timestamp should be recent (within last minute)
        time_diff = (datetime.utcnow() - response.timestamp).total_seconds()
        assert time_diff < 60

    def test_chat_response_json_serialization(self, sample_query_result):
        """Test that ChatResponse can be serialized to JSON"""
        response = ChatResponse(
            success=True,
            query="Test query",
            conversation_id="test-123",
            result=QueryResult(**sample_query_result),
            processing_time_ms=100.0
        )

        # Test model_dump
        data = response.model_dump()
        assert isinstance(data, dict)
        assert data['success'] is True
        assert data['query'] == "Test query"
        assert 'timestamp' in data

        # Test model_dump_json
        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        assert "Test query" in json_str

    def test_chat_response_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing"""
        with pytest.raises(ValidationError) as exc_info:
            ChatResponse(
                success=True
                # Missing query and conversation_id
            )

        error_str = str(exc_info.value)
        assert "query" in error_str or "conversation_id" in error_str


class TestAmbiguityResponse:
    """Test AmbiguityResponse schema"""

    def test_ambiguity_response_complete(self):
        """Test AmbiguityResponse with all fields"""
        response = AmbiguityResponse(
            query="Show me the metrics",
            reasons=[
                "Multiple possible metric interpretations",
                "Missing time period specification"
            ],
            suggestions=[
                "Specify which metrics (e.g., exposure, delinquency rate)",
                "Specify a time period (e.g., 'as of latest date')"
            ]
        )

        assert response.success is False  # Always False
        assert response.is_ambiguous is True  # Always True
        assert response.query == "Show me the metrics"
        assert len(response.reasons) == 2
        assert len(response.suggestions) == 2
        assert isinstance(response.timestamp, datetime)

    def test_ambiguity_response_always_false_success(self):
        """Test that success field is always False for AmbiguityResponse"""
        response = AmbiguityResponse(
            query="Test",
            reasons=["Reason"],
            suggestions=["Suggestion"]
        )

        # success should be False by default
        assert response.success is False

    def test_ambiguity_response_always_true_is_ambiguous(self):
        """Test that is_ambiguous field is always True for AmbiguityResponse"""
        response = AmbiguityResponse(
            query="Test",
            reasons=["Reason"],
            suggestions=["Suggestion"]
        )

        # is_ambiguous should be True by default
        assert response.is_ambiguous is True

    def test_ambiguity_response_json_serialization(self):
        """Test AmbiguityResponse JSON serialization"""
        response = AmbiguityResponse(
            query="Test query",
            reasons=["Reason 1"],
            suggestions=["Suggestion 1"]
        )

        data = response.model_dump()
        assert data['success'] is False
        assert data['is_ambiguous'] is True
        assert 'timestamp' in data

    def test_ambiguity_response_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing"""
        with pytest.raises(ValidationError) as exc_info:
            AmbiguityResponse(
                query="Test"
                # Missing reasons and suggestions
            )

        error_str = str(exc_info.value)
        assert "reasons" in error_str or "suggestions" in error_str


class TestErrorResponse:
    """Test ErrorResponse schema"""

    def test_error_response_complete(self):
        """Test ErrorResponse with all fields"""
        response = ErrorResponse(
            error="Failed to generate SQL query",
            error_type="SQLGenerationError",
            details={
                "original_error": "Invalid metric name",
                "metric": "unknown_metric"
            }
        )

        assert response.success is False  # Always False
        assert response.error == "Failed to generate SQL query"
        assert response.error_type == "SQLGenerationError"
        assert response.details is not None
        assert response.details['original_error'] == "Invalid metric name"
        assert isinstance(response.timestamp, datetime)

    def test_error_response_without_details(self):
        """Test ErrorResponse without optional details"""
        response = ErrorResponse(
            error="Something went wrong",
            error_type="InternalError"
        )

        assert response.error == "Something went wrong"
        assert response.error_type == "InternalError"
        assert response.details is None

    def test_error_response_always_false_success(self):
        """Test that success field is always False for ErrorResponse"""
        response = ErrorResponse(
            error="Test error",
            error_type="TestError"
        )

        assert response.success is False

    def test_error_response_json_serialization(self):
        """Test ErrorResponse JSON serialization"""
        response = ErrorResponse(
            error="Test error",
            error_type="TestError",
            details={"key": "value"}
        )

        data = response.model_dump()
        assert data['success'] is False
        assert data['error'] == "Test error"
        assert data['error_type'] == "TestError"
        assert 'timestamp' in data

    def test_error_response_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing"""
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(
                error="Test error"
                # Missing error_type
            )

        error_str = str(exc_info.value)
        assert "error_type" in error_str


class TestHealthResponse:
    """Test HealthResponse schema"""

    def test_health_response_complete(self):
        """Test HealthResponse with all fields"""
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            components={
                "database": "healthy",
                "llm": "healthy",
                "context_loader": "healthy"
            }
        )

        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert len(response.components) == 3
        assert response.components['database'] == "healthy"
        assert isinstance(response.timestamp, datetime)

    def test_health_response_unhealthy_status(self):
        """Test HealthResponse with unhealthy status"""
        response = HealthResponse(
            status="unhealthy",
            version="1.0.0",
            components={
                "database": "unhealthy",
                "llm": "healthy"
            }
        )

        assert response.status == "unhealthy"
        assert response.components['database'] == "unhealthy"

    def test_health_response_json_serialization(self):
        """Test HealthResponse JSON serialization"""
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            components={"db": "ok"}
        )

        data = response.model_dump()
        assert data['status'] == "healthy"
        assert 'timestamp' in data

    def test_health_response_missing_required_fields(self):
        """Test that ValidationError is raised when required fields are missing"""
        with pytest.raises(ValidationError) as exc_info:
            HealthResponse(
                status="healthy"
                # Missing version and components
            )

        error_str = str(exc_info.value)
        assert "version" in error_str or "components" in error_str


class TestSchemaEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_chat_request_query_exactly_1_char(self):
        """Test ChatRequest with query of exactly 1 character"""
        request = ChatRequest(query="a")
        assert len(request.query) == 1

    def test_query_result_with_large_results_list(self):
        """Test QueryResult with large results list"""
        large_results = [{"id": i, "value": f"value_{i}"} for i in range(1000)]

        result = QueryResult(
            sql="SELECT * FROM large_table",
            explanation="Large result set",
            results=large_results,
            metrics_used=["metric1"],
            visualization_hint="table",
            row_count=len(large_results)
        )

        assert result.row_count == 1000
        assert len(result.results) == 1000

    def test_empty_strings_in_optional_fields(self):
        """Test handling of empty strings in optional fields"""
        response = ChatResponse(
            success=True,
            query="Test",
            conversation_id="",  # Empty string
            result=None
        )

        assert response.conversation_id == ""

    def test_none_values_for_optional_fields(self):
        """Test None values for optional fields"""
        response = ChatResponse(
            success=True,
            query="Test",
            conversation_id="test-123",
            result=None,
            error=None,
            suggestions=None,
            processing_time_ms=None
        )

        assert response.result is None
        assert response.error is None
        assert response.suggestions is None
        assert response.processing_time_ms is None
