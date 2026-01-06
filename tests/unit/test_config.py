"""
Unit Tests for Configuration Management (app/config.py)

Tests configuration loading, validation, and defaults
"""

import pytest
from pydantic import ValidationError
from app.config import Settings


class TestSettingsValidation:
    """Test Settings validation and loading"""

    def test_settings_load_from_env(self, test_env_vars):
        """Test that settings load correctly from environment variables"""
        settings = Settings()

        assert settings.APP_NAME == "CR360 Test"
        assert settings.APP_VERSION == "1.0.0-test"
        assert settings.SUPABASE_URL == "https://test.supabase.co"
        assert settings.SUPABASE_KEY == "test_key_123"
        assert settings.DATABASE_URL == "postgresql://test:test@localhost:5432/test_db"
        assert settings.GOOGLE_API_KEY == "test_google_api_key"
        assert settings.LLM_MODEL == "gemini-2.5-flash-preview"

    def test_settings_defaults(self, test_env_vars):
        """Test that default values are applied correctly"""
        settings = Settings()

        # Check default values
        assert settings.APP_NAME == "CR360 Test"  # From env
        assert settings.APP_VERSION == "1.0.0-test"  # From env
        assert settings.LOG_LEVEL == "INFO"
        assert settings.LLM_TEMPERATURE == 0.1
        assert settings.LLM_MAX_TOKENS == 8192
        assert settings.MAX_CONVERSATION_TURNS == 5
        assert settings.RATE_LIMIT_PER_MINUTE == 60

    def test_settings_required_fields_missing(self, monkeypatch):
        """Test that ValidationError is raised when required fields are missing"""
        # Clear ALL environment variables to start fresh
        import os
        for key in list(os.environ.keys()):
            if key.startswith(('SUPABASE_', 'DATABASE_', 'GOOGLE_', 'CONTEXT_', 'LLM_', 'APP_', 'REDIS_', 'CORS_', 'RATE_')):
                monkeypatch.delenv(key, raising=False)

        # Import Settings class (not instance) and instantiate AFTER env modifications
        from app.config import Settings

        # Attempt to create Settings without required fields
        # Pass _env_file=None to prevent loading from .env file
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        # Check that the error mentions at least one of the missing required fields
        error_str = str(exc_info.value)
        assert ("SUPABASE_URL" in error_str or "SUPABASE_KEY" in error_str or
                "DATABASE_URL" in error_str or "GOOGLE_API_KEY" in error_str)

    def test_settings_type_conversion_int(self, test_env_vars, monkeypatch):
        """Test that integer types are converted correctly"""
        monkeypatch.setenv("LLM_MAX_TOKENS", "4096")
        monkeypatch.setenv("MAX_CONVERSATION_TURNS", "10")
        monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "120")

        settings = Settings()

        assert isinstance(settings.LLM_MAX_TOKENS, int)
        assert settings.LLM_MAX_TOKENS == 4096
        assert isinstance(settings.MAX_CONVERSATION_TURNS, int)
        assert settings.MAX_CONVERSATION_TURNS == 10
        assert isinstance(settings.RATE_LIMIT_PER_MINUTE, int)
        assert settings.RATE_LIMIT_PER_MINUTE == 120

    def test_settings_type_conversion_float(self, test_env_vars, monkeypatch):
        """Test that float types are converted correctly"""
        monkeypatch.setenv("LLM_TEMPERATURE", "0.5")

        settings = Settings()

        assert isinstance(settings.LLM_TEMPERATURE, float)
        assert settings.LLM_TEMPERATURE == 0.5

    def test_settings_type_conversion_bool(self, test_env_vars, monkeypatch):
        """Test that boolean types are converted correctly"""
        monkeypatch.setenv("DEBUG", "false")

        settings = Settings()

        assert isinstance(settings.DEBUG, bool)
        assert settings.DEBUG is False

        # Test with string "true"
        monkeypatch.setenv("DEBUG", "true")
        settings = Settings()
        assert settings.DEBUG is True

    def test_cors_origins_as_string(self, test_env_vars):
        """Test that CORS origins are stored as comma-separated string"""
        settings = Settings()

        assert isinstance(settings.CORS_ORIGINS, str)
        assert "http://localhost:3000" in settings.CORS_ORIGINS
        assert "http://localhost:8000" in settings.CORS_ORIGINS

    def test_redis_url_optional(self, monkeypatch):
        """Test that REDIS_URL is optional and defaults to None"""
        # Set only required fields, not REDIS_URL
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test_key")
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
        monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")
        monkeypatch.delenv("REDIS_URL", raising=False)

        from app.config import Settings
        # Pass _env_file=None to prevent loading from .env file
        settings = Settings(_env_file=None)

        # REDIS_URL should be None when not set
        assert settings.REDIS_URL is None

    def test_context_file_path_default(self, test_env_vars, monkeypatch):
        """Test that CONTEXT_FILE_PATH has correct default"""
        # Don't set CONTEXT_FILE_PATH in environment
        monkeypatch.delenv("CONTEXT_FILE_PATH", raising=False)

        settings = Settings()

        assert settings.CONTEXT_FILE_PATH == "./context/cr360_semantic_model_v2.yaml"


class TestSettingsEdgeCases:
    """Test edge cases and error scenarios"""

    def test_settings_invalid_type_for_int_field(self, test_env_vars, monkeypatch):
        """Test that invalid types for integer fields raise ValidationError"""
        monkeypatch.setenv("LLM_MAX_TOKENS", "not_a_number")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value)
        assert "LLM_MAX_TOKENS" in error_str

    def test_settings_invalid_type_for_float_field(self, test_env_vars, monkeypatch):
        """Test that invalid types for float fields raise ValidationError"""
        monkeypatch.setenv("LLM_TEMPERATURE", "not_a_float")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value)
        assert "LLM_TEMPERATURE" in error_str

    def test_settings_empty_string_for_required_field(self, monkeypatch):
        """Test that empty strings are accepted (Pydantic allows empty str for str fields)"""
        # Set all required fields, one with empty string
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test_key")
        monkeypatch.setenv("DATABASE_URL", "")  # Empty string for required field
        monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")

        from app.config import Settings

        # Pydantic str fields accept empty strings by default (no min_length constraint)
        # So this should succeed, not raise ValidationError
        settings = Settings(_env_file=None)
        assert settings.DATABASE_URL == ""  # Empty string is stored as-is

    def test_settings_case_sensitivity(self, test_env_vars, monkeypatch):
        """Test that environment variable names are case sensitive"""
        # Set lowercase version (should not be recognized)
        monkeypatch.setenv("app_name", "WrongName")
        monkeypatch.setenv("APP_NAME", "CorrectName")

        settings = Settings()

        # Should use the correctly cased version
        assert settings.APP_NAME == "CorrectName"


class TestSettingsMultipleInstances:
    """Test behavior with multiple Settings instances"""

    def test_settings_multiple_instances_share_env(self, test_env_vars):
        """Test that multiple Settings instances read same environment"""
        settings1 = Settings()
        settings2 = Settings()

        assert settings1.APP_NAME == settings2.APP_NAME
        assert settings1.SUPABASE_URL == settings2.SUPABASE_URL
        assert settings1.GOOGLE_API_KEY == settings2.GOOGLE_API_KEY

    def test_settings_env_change_not_reflected(self, test_env_vars, monkeypatch):
        """Test that changing environment after Settings creation doesn't affect instance"""
        settings = Settings()
        original_app_name = settings.APP_NAME

        # Change environment variable
        monkeypatch.setenv("APP_NAME", "NewName")

        # Original settings instance should not change
        assert settings.APP_NAME == original_app_name

        # New instance should pick up the change
        settings_new = Settings()
        assert settings_new.APP_NAME == "NewName"
