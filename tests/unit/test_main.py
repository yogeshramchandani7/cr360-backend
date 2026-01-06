"""
Unit Tests for Main Application (app/main.py)

Tests FastAPI app initialization, middleware, and router configuration
"""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.main import app


class TestAppInitialization:
    """Test FastAPI application initialization"""

    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance"""
        assert isinstance(app, FastAPI)

    def test_app_title(self):
        """Test that app has correct title"""
        assert "CR360" in app.title

    def test_app_version(self):
        """Test that app has version set"""
        assert app.version is not None
        assert len(app.version) > 0

    def test_app_description(self):
        """Test that app has description"""
        assert app.description is not None
        assert "Credit Risk" in app.description or "CR360" in app.description


class TestCORSMiddleware:
    """Test CORS middleware configuration"""

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is added to app"""
        # Check if CORSMiddleware is in the app's middleware stack
        has_cors = any(
            hasattr(middleware, 'cls') and middleware.cls == CORSMiddleware
            for middleware in app.user_middleware
        )
        assert has_cors, "CORS middleware not configured"

    def test_cors_allows_all_methods(self):
        """Test that CORS allows all methods"""
        cors_middleware = None
        for middleware in app.user_middleware:
            if hasattr(middleware, 'cls') and middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None
        # Check that options include allow_methods=["*"]
        options = cors_middleware.options
        assert options.get('allow_methods') == ['*']

    def test_cors_allows_all_headers(self):
        """Test that CORS allows all headers"""
        cors_middleware = None
        for middleware in app.user_middleware:
            if hasattr(middleware, 'cls') and middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None
        options = cors_middleware.options
        assert options.get('allow_headers') == ['*']


class TestRouters:
    """Test router configuration"""

    def test_routers_included(self):
        """Test that routers are included in the app"""
        # Get all routes
        routes = [route.path for route in app.routes]

        # Check for health endpoint
        assert any('/health' in route for route in routes), "Health router not included"

        # Check for chat endpoint
        assert any('/chat' in route or '/api/v1/chat' in route for route in routes), "Chat router not included"

    def test_app_has_routes(self):
        """Test that app has routes registered"""
        assert len(app.routes) > 0, "No routes registered"

    def test_health_endpoint_exists(self):
        """Test that health endpoint is accessible"""
        routes = {route.path: route for route in app.routes}

        # Health endpoint should exist
        health_paths = [path for path in routes.keys() if 'health' in path.lower()]
        assert len(health_paths) > 0, "Health endpoint not found"

    def test_chat_endpoint_exists(self):
        """Test that chat endpoint is accessible"""
        routes = {route.path: route for route in app.routes}

        # Chat endpoint should exist
        chat_paths = [path for path in routes.keys() if 'chat' in path.lower()]
        assert len(chat_paths) > 0, "Chat endpoint not found"


class TestLifespan:
    """Test application lifespan"""

    def test_app_has_lifespan(self):
        """Test that app has lifespan configured"""
        assert app.router.lifespan_context is not None, "Lifespan not configured"


class TestAppMetadata:
    """Test application metadata"""

    def test_app_openapi_url(self):
        """Test that OpenAPI URL is configured"""
        assert app.openapi_url is not None

    def test_app_docs_url(self):
        """Test that Swagger docs URL is available"""
        assert app.docs_url is not None

    def test_app_redoc_url(self):
        """Test that ReDoc URL is available"""
        assert app.redoc_url is not None
