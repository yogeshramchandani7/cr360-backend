"""
Unit Tests for Health Route (app/api/routes/health.py)

Tests health check endpoints with mocked dependencies
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import status
from app.api.routes.health import health_check, root, router


class TestHealthCheckEndpoint:
    """Test health_check endpoint"""

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_check_all_healthy(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db
    ):
        """Test health check when all components are healthy"""
        # Mock database
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        # Mock context loader
        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        # Mock settings
        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = await health_check()

        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.components['database'] == 'healthy'
        assert response.components['context_loader'] == 'healthy'
        assert response.components['llm'] in ['configured', 'healthy']

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_check_database_unhealthy(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db
    ):
        """Test health check when database is unhealthy"""
        # Mock database failure
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(side_effect=Exception("Connection failed"))
        mock_get_db.return_value = mock_db_client

        # Mock context loader (healthy)
        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        # Mock settings
        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = await health_check()

        assert response.status == "unhealthy"
        assert response.components['database'] == 'unhealthy'

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_check_context_loader_unhealthy(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db
    ):
        """Test health check when context loader is unhealthy"""
        # Mock database (healthy)
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        # Mock context loader failure
        mock_get_context.side_effect = Exception("Failed to load context")

        # Mock settings
        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = await health_check()

        assert response.status == "unhealthy"
        assert response.components['context_loader'] == 'unhealthy'

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_check_llm_not_configured(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db
    ):
        """Test health check when LLM is not configured"""
        # Mock database (healthy)
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        # Mock context loader (healthy)
        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        # Mock settings without API key
        mock_settings.GOOGLE_API_KEY = None
        mock_settings.APP_VERSION = "1.0.0"

        response = await health_check()

        assert response.status == "unhealthy"
        assert response.components['llm'] == 'not_configured'

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_check_context_loader_loads_if_not_loaded(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db
    ):
        """Test that health check loads context if not already loaded"""
        # Mock database
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        # Mock context loader (not loaded)
        mock_context_loader = Mock()
        mock_context_loader._loaded = False
        mock_context_loader.load = Mock()
        mock_get_context.return_value = mock_context_loader

        # Mock settings
        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = await health_check()

        # Verify load was called
        mock_context_loader.load.assert_called_once()
        assert response.components['context_loader'] == 'healthy'


class TestRootEndpoint:
    """Test root endpoint"""

    @pytest.mark.asyncio
    @patch('app.api.routes.health.settings')
    async def test_root_endpoint(self, mock_settings):
        """Test root endpoint returns correct response"""
        mock_settings.APP_NAME = "CR360"
        mock_settings.APP_VERSION = "1.0.0"

        response = await root()

        assert 'message' in response
        assert 'CR360' in response['message']
        assert response['version'] == "1.0.0"
        assert response['status'] == "running"

    @pytest.mark.asyncio
    async def test_root_endpoint_structure(self):
        """Test that root endpoint has correct structure"""
        response = await root()

        assert isinstance(response, dict)
        assert 'message' in response
        assert 'version' in response
        assert 'status' in response


class TestRouterConfiguration:
    """Test router configuration"""

    def test_router_has_health_tag(self):
        """Test that router has 'health' tag"""
        assert 'health' in router.tags

    def test_health_endpoint_path(self):
        """Test health endpoint is at /health"""
        routes = {route.path: route for route in router.routes}
        assert '/health' in routes

    def test_root_endpoint_path(self):
        """Test root endpoint is at /"""
        routes = {route.path: route for route in router.routes}
        assert '/' in routes

    def test_health_endpoint_method(self):
        """Test health endpoint accepts GET method"""
        health_route = None
        for route in router.routes:
            if route.path == '/health':
                health_route = route
                break

        assert health_route is not None
        assert 'GET' in health_route.methods

    def test_root_endpoint_method(self):
        """Test root endpoint accepts GET method"""
        root_route = None
        for route in router.routes:
            if route.path == '/':
                root_route = route
                break

        assert root_route is not None
        assert 'GET' in root_route.methods
