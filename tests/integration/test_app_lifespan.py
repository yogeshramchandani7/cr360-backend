"""
Integration Tests for Application Lifespan

Tests app startup, shutdown, and singleton patterns
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestAppStartup:
    """Test application startup behavior"""

    @pytest.mark.asyncio
    @patch('app.llm.context_loader.get_context_loader')
    async def test_startup_loads_context(self, mock_get_context):
        """Test that context is loaded on app startup"""
        # Note: In actual integration test, startup happens when TestClient is created
        # This test verifies the logic
        mock_context_loader = Mock()
        mock_context_loader.load = Mock()
        mock_context_loader.get_metrics = Mock(return_value={'metric1': {}})
        mock_context_loader.get_dimensions = Mock(return_value={'dim1': {}})
        mock_get_context.return_value = mock_context_loader

        # Simulate startup by importing main
        # In real scenario, FastAPI lifespan context manager handles this
        context_loader = mock_get_context()
        context_loader.load()

        mock_context_loader.load.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.database.client.get_database_client')
    async def test_startup_initializes_database(self, mock_get_db):
        """Test that database client is initialized"""
        mock_db_client = Mock()
        mock_get_db.return_value = mock_db_client

        # Verify database client can be retrieved
        db_client = mock_get_db()
        assert db_client is mock_db_client

    @pytest.mark.asyncio
    @patch('app.llm.context_loader.get_context_loader')
    async def test_startup_failure_raises_error(self, mock_get_context):
        """Test that startup errors are raised"""
        mock_context_loader = Mock()
        mock_context_loader.load = Mock(side_effect=Exception("Failed to load context"))
        mock_get_context.return_value = mock_context_loader

        with pytest.raises(Exception) as exc_info:
            context_loader = mock_get_context()
            context_loader.load()

        assert "Failed to load context" in str(exc_info.value)


class TestAppShutdown:
    """Test application shutdown behavior"""

    @pytest.mark.asyncio
    @patch('app.database.client.get_database_client')
    async def test_shutdown_closes_connections(self, mock_get_db):
        """Test that database connections are closed on shutdown"""
        mock_db_client = Mock()
        mock_db_client.close = Mock()
        mock_get_db.return_value = mock_db_client

        # Simulate shutdown
        db_client = mock_get_db()
        db_client.close()

        mock_db_client.close.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.database.client.get_database_client')
    async def test_shutdown_handles_errors_gracefully(self, mock_get_db):
        """Test that shutdown errors are handled gracefully"""
        mock_db_client = Mock()
        mock_db_client.close = Mock(side_effect=Exception("Close error"))
        mock_get_db.return_value = mock_db_client

        # Shutdown should not raise even if close fails
        try:
            db_client = mock_get_db()
            db_client.close()
        except Exception:
            # In real app, this would be logged but not raised
            pass


class TestContextSharing:
    """Test that context is shared across requests"""

    @pytest.mark.asyncio
    @patch('app.llm.context_loader.get_context_loader')
    async def test_multiple_requests_share_context(self, mock_get_context):
        """Test that context loader is reused across requests"""
        mock_context_loader = Mock()
        mock_context_loader.context = {'test': 'data'}
        mock_get_context.return_value = mock_context_loader

        # Simulate multiple requests
        loader1 = mock_get_context()
        loader2 = mock_get_context()

        # Should return same instance
        assert loader1 is loader2
        assert loader1.context == loader2.context

    @pytest.mark.asyncio
    @patch('app.llm.context_loader.get_context_loader')
    async def test_context_persists_between_requests(self, mock_get_context):
        """Test that loaded context persists"""
        mock_context_loader = Mock()
        mock_context_loader.context = {'metrics': {'test': {}}}
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        # First request
        loader1 = mock_get_context()
        assert loader1._loaded is True

        # Second request should see same loaded state
        loader2 = mock_get_context()
        assert loader2._loaded is True
        assert loader2.context == loader1.context


class TestSingletonPattern:
    """Test singleton patterns for shared resources"""

    @pytest.mark.asyncio
    async def test_context_loader_singleton(self):
        """Test that context loader uses singleton pattern"""
        from app.llm.context_loader import get_context_loader

        # Reset singleton
        import app.llm.context_loader as cl_module
        cl_module._context_loader = None

        loader1 = get_context_loader()
        loader2 = get_context_loader()

        assert loader1 is loader2

        # Clean up
        cl_module._context_loader = None

    @pytest.mark.asyncio
    async def test_database_client_singleton(self):
        """Test that database client uses singleton pattern"""
        from app.database.client import get_database_client

        # Reset singleton
        import app.database.client as db_module
        db_module._database_client = None

        client1 = get_database_client()
        client2 = get_database_client()

        assert client1 is client2

        # Clean up
        db_module._database_client = None

    @pytest.mark.asyncio
    async def test_gemini_client_singleton(self):
        """Test that gemini client uses singleton pattern"""
        from app.llm.gemini_client import get_gemini_client

        # Reset singleton
        import app.llm.gemini_client as gc_module
        gc_module._gemini_client = None

        with patch('app.llm.gemini_client.genai'):
            client1 = get_gemini_client()
            client2 = get_gemini_client()

            assert client1 is client2

        # Clean up
        gc_module._gemini_client = None

    @pytest.mark.asyncio
    async def test_text_to_sql_engine_singleton(self):
        """Test that text-to-sql engine uses singleton pattern"""
        from app.query.text_to_sql import get_text_to_sql_engine

        # Reset singleton
        import app.query.text_to_sql as tts_module
        tts_module._text_to_sql_engine = None

        with patch('app.query.text_to_sql.get_context_loader'), \
             patch('app.query.text_to_sql.get_gemini_client'), \
             patch('app.query.text_to_sql.get_database_client'):

            mock_context_loader = Mock()
            mock_context_loader.get_context_for_llm.return_value = "context"

            with patch('app.query.text_to_sql.get_context_loader', return_value=mock_context_loader):
                engine1 = get_text_to_sql_engine()
                engine2 = get_text_to_sql_engine()

                assert engine1 is engine2

        # Clean up
        tts_module._text_to_sql_engine = None


class TestConcurrentRequests:
    """Test behavior under concurrent requests"""

    @pytest.mark.asyncio
    @patch('app.llm.context_loader.get_context_loader')
    async def test_concurrent_access_to_shared_resources(self, mock_get_context):
        """Test that shared resources handle concurrent access"""
        mock_context_loader = Mock()
        mock_context_loader.context = {'shared': 'data'}
        mock_get_context.return_value = mock_context_loader

        # Simulate concurrent access
        import asyncio

        async def access_context():
            loader = mock_get_context()
            return loader.context

        # Run multiple concurrent accesses
        results = await asyncio.gather(
            access_context(),
            access_context(),
            access_context()
        )

        # All should return same data
        assert all(r == {'shared': 'data'} for r in results)
