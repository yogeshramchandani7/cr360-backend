"""
Integration Tests for Health Endpoint

Tests health check API with real HTTP requests
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import status


class TestHealthEndpointIntegration:
    """Integration tests for /health endpoint"""

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_endpoint_returns_200(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db,
        test_client
    ):
        """Test health endpoint returns 200 OK"""
        # Mock dependencies
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = test_client.get("/health")

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_response_format(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db,
        test_client
    ):
        """Test that health response has correct JSON format"""
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = test_client.get("/health")

        data = response.json()
        assert isinstance(data, dict)
        assert 'status' in data
        assert 'version' in data
        assert 'components' in data
        assert 'timestamp' in data

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_includes_version(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db,
        test_client
    ):
        """Test that health response includes app version"""
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0-test"

        response = test_client.get("/health")

        data = response.json()
        assert data['version'] == "1.0.0-test"

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_checks_database(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db,
        test_client
    ):
        """Test that health check tests database connection"""
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = test_client.get("/health")

        data = response.json()
        assert 'database' in data['components']
        assert data['components']['database'] in ['healthy', 'unhealthy']

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_checks_context_loader(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db,
        test_client
    ):
        """Test that health check tests context loader"""
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = test_client.get("/health")

        data = response.json()
        assert 'context_loader' in data['components']
        assert data['components']['context_loader'] in ['healthy', 'unhealthy']

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_checks_llm(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db,
        test_client
    ):
        """Test that health check verifies LLM configuration"""
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(return_value=True)
        mock_get_db.return_value = mock_db_client

        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = test_client.get("/health")

        data = response.json()
        assert 'llm' in data['components']
        assert data['components']['llm'] in ['configured', 'not_configured', 'error']

    @pytest.mark.asyncio
    @patch('app.api.routes.health.get_database_client')
    @patch('app.api.routes.health.get_context_loader')
    @patch('app.api.routes.health.settings')
    async def test_health_unhealthy_component(
        self,
        mock_settings,
        mock_get_context,
        mock_get_db,
        test_client
    ):
        """Test that overall status is unhealthy if any component fails"""
        # Mock database failure
        mock_db_client = Mock()
        mock_db_client.test_connection = AsyncMock(side_effect=Exception("DB Error"))
        mock_get_db.return_value = mock_db_client

        mock_context_loader = Mock()
        mock_context_loader._loaded = True
        mock_get_context.return_value = mock_context_loader

        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.APP_VERSION = "1.0.0"

        response = test_client.get("/health")

        data = response.json()
        assert data['status'] == 'unhealthy'
        assert data['components']['database'] == 'unhealthy'


class TestRootEndpointIntegration:
    """Integration tests for / (root) endpoint"""

    @pytest.mark.asyncio
    @patch('app.api.routes.health.settings')
    async def test_root_endpoint_accessible(self, mock_settings, test_client):
        """Test that root endpoint is accessible"""
        mock_settings.APP_NAME = "CR360"
        mock_settings.APP_VERSION = "1.0.0"

        response = test_client.get("/")

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch('app.api.routes.health.settings')
    async def test_root_endpoint_returns_welcome_message(self, mock_settings, test_client):
        """Test that root endpoint returns welcome message"""
        mock_settings.APP_NAME = "CR360"
        mock_settings.APP_VERSION = "1.0.0"

        response = test_client.get("/")

        data = response.json()
        assert 'message' in data
        assert 'version' in data
        assert 'status' in data
        assert data['status'] == 'running'
