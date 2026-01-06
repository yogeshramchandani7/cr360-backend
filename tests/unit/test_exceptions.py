"""
Unit Tests for Custom Exceptions (app/utils/exceptions.py)

Tests exception hierarchy, initialization, and behavior
"""

import pytest
from app.utils.exceptions import (
    CR360Exception,
    ConfigurationError,
    DatabaseError,
    LLMError,
    SQLGenerationError,
    SQLValidationError,
    SQLExecutionError,
    ContextLoadError,
    AmbiguousQueryError
)


class TestBaseException:
    """Test CR360Exception base class"""

    def test_cr360_exception_instantiation(self):
        """Test that CR360Exception can be instantiated"""
        exc = CR360Exception("Test error message")

        assert isinstance(exc, Exception)
        assert str(exc) == "Test error message"

    def test_cr360_exception_raise_and_catch(self):
        """Test that CR360Exception can be raised and caught"""
        with pytest.raises(CR360Exception) as exc_info:
            raise CR360Exception("Test error")

        assert str(exc_info.value) == "Test error"

    def test_cr360_exception_empty_message(self):
        """Test CR360Exception with empty message"""
        exc = CR360Exception("")

        assert str(exc) == ""


class TestConfigurationError:
    """Test ConfigurationError exception"""

    def test_configuration_error_instantiation(self):
        """Test ConfigurationError instantiation"""
        exc = ConfigurationError("Invalid configuration")

        assert isinstance(exc, CR360Exception)
        assert isinstance(exc, Exception)
        assert str(exc) == "Invalid configuration"

    def test_configuration_error_raise_and_catch(self):
        """Test raising and catching ConfigurationError"""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Missing API key")

        assert "Missing API key" in str(exc_info.value)

    def test_configuration_error_inheritance(self):
        """Test that ConfigurationError inherits from CR360Exception"""
        exc = ConfigurationError("Test")

        assert isinstance(exc, CR360Exception)


class TestDatabaseError:
    """Test DatabaseError exception"""

    def test_database_error_instantiation(self):
        """Test DatabaseError instantiation"""
        exc = DatabaseError("Database connection failed")

        assert isinstance(exc, CR360Exception)
        assert str(exc) == "Database connection failed"

    def test_database_error_raise_and_catch(self):
        """Test raising and catching DatabaseError"""
        with pytest.raises(DatabaseError) as exc_info:
            raise DatabaseError("Connection timeout")

        assert "Connection timeout" in str(exc_info.value)

    def test_database_error_inheritance(self):
        """Test that DatabaseError inherits from CR360Exception"""
        exc = DatabaseError("Test")

        assert isinstance(exc, CR360Exception)


class TestLLMError:
    """Test LLMError exception"""

    def test_llm_error_instantiation(self):
        """Test LLMError instantiation"""
        exc = LLMError("Gemini API call failed")

        assert isinstance(exc, CR360Exception)
        assert str(exc) == "Gemini API call failed"

    def test_llm_error_raise_and_catch(self):
        """Test raising and catching LLMError"""
        with pytest.raises(LLMError) as exc_info:
            raise LLMError("API quota exceeded")

        assert "API quota exceeded" in str(exc_info.value)

    def test_llm_error_inheritance(self):
        """Test that LLMError inherits from CR360Exception"""
        exc = LLMError("Test")

        assert isinstance(exc, CR360Exception)


class TestSQLGenerationError:
    """Test SQLGenerationError exception"""

    def test_sql_generation_error_instantiation(self):
        """Test SQLGenerationError instantiation"""
        exc = SQLGenerationError("Failed to generate SQL")

        assert isinstance(exc, LLMError)
        assert isinstance(exc, CR360Exception)
        assert str(exc) == "Failed to generate SQL"

    def test_sql_generation_error_raise_and_catch(self):
        """Test raising and catching SQLGenerationError"""
        with pytest.raises(SQLGenerationError) as exc_info:
            raise SQLGenerationError("Invalid metric in query")

        assert "Invalid metric in query" in str(exc_info.value)

    def test_sql_generation_error_inheritance_chain(self):
        """Test that SQLGenerationError inherits from LLMError and CR360Exception"""
        exc = SQLGenerationError("Test")

        assert isinstance(exc, SQLGenerationError)
        assert isinstance(exc, LLMError)
        assert isinstance(exc, CR360Exception)
        assert isinstance(exc, Exception)

    def test_sql_generation_error_caught_as_llm_error(self):
        """Test that SQLGenerationError can be caught as LLMError"""
        with pytest.raises(LLMError):
            raise SQLGenerationError("Test error")


class TestSQLValidationError:
    """Test SQLValidationError exception"""

    def test_sql_validation_error_instantiation(self):
        """Test SQLValidationError instantiation"""
        exc = SQLValidationError("SQL validation failed")

        assert isinstance(exc, CR360Exception)
        assert str(exc) == "SQL validation failed"

    def test_sql_validation_error_raise_and_catch(self):
        """Test raising and catching SQLValidationError"""
        with pytest.raises(SQLValidationError) as exc_info:
            raise SQLValidationError("Dangerous keyword detected: DROP")

        assert "Dangerous keyword detected" in str(exc_info.value)

    def test_sql_validation_error_inheritance(self):
        """Test that SQLValidationError inherits from CR360Exception"""
        exc = SQLValidationError("Test")

        assert isinstance(exc, CR360Exception)


class TestSQLExecutionError:
    """Test SQLExecutionError exception"""

    def test_sql_execution_error_instantiation(self):
        """Test SQLExecutionError instantiation"""
        exc = SQLExecutionError("SQL execution failed")

        assert isinstance(exc, DatabaseError)
        assert isinstance(exc, CR360Exception)
        assert str(exc) == "SQL execution failed"

    def test_sql_execution_error_raise_and_catch(self):
        """Test raising and catching SQLExecutionError"""
        with pytest.raises(SQLExecutionError) as exc_info:
            raise SQLExecutionError("Syntax error near WHERE")

        assert "Syntax error" in str(exc_info.value)

    def test_sql_execution_error_inheritance_chain(self):
        """Test that SQLExecutionError inherits from DatabaseError and CR360Exception"""
        exc = SQLExecutionError("Test")

        assert isinstance(exc, SQLExecutionError)
        assert isinstance(exc, DatabaseError)
        assert isinstance(exc, CR360Exception)
        assert isinstance(exc, Exception)

    def test_sql_execution_error_caught_as_database_error(self):
        """Test that SQLExecutionError can be caught as DatabaseError"""
        with pytest.raises(DatabaseError):
            raise SQLExecutionError("Test error")


class TestContextLoadError:
    """Test ContextLoadError exception"""

    def test_context_load_error_instantiation(self):
        """Test ContextLoadError instantiation"""
        exc = ContextLoadError("Failed to load semantic model")

        assert isinstance(exc, CR360Exception)
        assert str(exc) == "Failed to load semantic model"

    def test_context_load_error_raise_and_catch(self):
        """Test raising and catching ContextLoadError"""
        with pytest.raises(ContextLoadError) as exc_info:
            raise ContextLoadError("YAML parse error")

        assert "YAML parse error" in str(exc_info.value)

    def test_context_load_error_inheritance(self):
        """Test that ContextLoadError inherits from CR360Exception"""
        exc = ContextLoadError("Test")

        assert isinstance(exc, CR360Exception)


class TestAmbiguousQueryError:
    """Test AmbiguousQueryError exception with options"""

    def test_ambiguous_query_error_instantiation_with_options(self):
        """Test AmbiguousQueryError with options list"""
        options = [
            "Specify a time period",
            "Specify a product type"
        ]
        exc = AmbiguousQueryError("Your query is ambiguous", options=options)

        assert isinstance(exc, CR360Exception)
        assert str(exc) == "Your query is ambiguous"
        assert exc.options == options
        assert len(exc.options) == 2

    def test_ambiguous_query_error_instantiation_without_options(self):
        """Test AmbiguousQueryError without options (defaults to empty list)"""
        exc = AmbiguousQueryError("Your query is ambiguous")

        assert isinstance(exc, CR360Exception)
        assert str(exc) == "Your query is ambiguous"
        assert exc.options == []
        assert isinstance(exc.options, list)

    def test_ambiguous_query_error_raise_and_catch(self):
        """Test raising and catching AmbiguousQueryError"""
        options = ["Suggestion 1", "Suggestion 2"]

        with pytest.raises(AmbiguousQueryError) as exc_info:
            raise AmbiguousQueryError("Ambiguous query", options=options)

        assert "Ambiguous query" in str(exc_info.value)
        assert exc_info.value.options == options

    def test_ambiguous_query_error_options_access(self):
        """Test accessing options attribute"""
        options = ["Option A", "Option B", "Option C"]
        exc = AmbiguousQueryError("Test", options=options)

        assert len(exc.options) == 3
        assert exc.options[0] == "Option A"
        assert exc.options[1] == "Option B"
        assert exc.options[2] == "Option C"

    def test_ambiguous_query_error_empty_options_list(self):
        """Test AmbiguousQueryError with explicitly empty options list"""
        exc = AmbiguousQueryError("Test", options=[])

        assert exc.options == []
        assert isinstance(exc.options, list)

    def test_ambiguous_query_error_inheritance(self):
        """Test that AmbiguousQueryError inherits from CR360Exception"""
        exc = AmbiguousQueryError("Test", options=["Opt1"])

        assert isinstance(exc, CR360Exception)


class TestExceptionStringConversion:
    """Test string conversion for all exceptions"""

    def test_exception_str_conversion(self):
        """Test that str() returns the message for all exceptions"""
        exceptions = [
            (CR360Exception("msg1"), "msg1"),
            (ConfigurationError("msg2"), "msg2"),
            (DatabaseError("msg3"), "msg3"),
            (LLMError("msg4"), "msg4"),
            (SQLGenerationError("msg5"), "msg5"),
            (SQLValidationError("msg6"), "msg6"),
            (SQLExecutionError("msg7"), "msg7"),
            (ContextLoadError("msg8"), "msg8"),
            (AmbiguousQueryError("msg9", options=["opt"]), "msg9"),
        ]

        for exc, expected_msg in exceptions:
            assert str(exc) == expected_msg


class TestExceptionHierarchy:
    """Test exception hierarchy and catching behavior"""

    def test_catch_specific_exception(self):
        """Test catching specific exception types"""
        with pytest.raises(SQLGenerationError):
            raise SQLGenerationError("Test")

    def test_catch_parent_exception(self):
        """Test catching child exception with parent type"""
        # SQLGenerationError should be caught by LLMError
        with pytest.raises(LLMError):
            raise SQLGenerationError("Test")

        # SQLExecutionError should be caught by DatabaseError
        with pytest.raises(DatabaseError):
            raise SQLExecutionError("Test")

    def test_catch_base_exception(self):
        """Test that all custom exceptions can be caught with CR360Exception"""
        exceptions = [
            ConfigurationError("test"),
            DatabaseError("test"),
            LLMError("test"),
            SQLGenerationError("test"),
            SQLValidationError("test"),
            SQLExecutionError("test"),
            ContextLoadError("test"),
            AmbiguousQueryError("test")
        ]

        for exc in exceptions:
            with pytest.raises(CR360Exception):
                raise exc

    def test_exception_not_caught_by_wrong_type(self):
        """Test that exceptions are not caught by unrelated types"""
        # SQLGenerationError should not be caught by DatabaseError
        with pytest.raises(SQLGenerationError):
            try:
                raise SQLGenerationError("Test")
            except DatabaseError:
                pytest.fail("Should not catch SQLGenerationError as DatabaseError")

        # ConfigurationError should not be caught by LLMError
        with pytest.raises(ConfigurationError):
            try:
                raise ConfigurationError("Test")
            except LLMError:
                pytest.fail("Should not catch ConfigurationError as LLMError")
