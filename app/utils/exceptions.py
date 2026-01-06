"""
Custom exceptions for CR360 backend
"""


class CR360Exception(Exception):
    """Base exception for CR360 application"""

    pass


class ConfigurationError(CR360Exception):
    """Raised when configuration is invalid"""

    pass


class DatabaseError(CR360Exception):
    """Raised when database operations fail"""

    pass


class LLMError(CR360Exception):
    """Raised when LLM API calls fail"""

    pass


class SQLGenerationError(LLMError):
    """Raised when SQL generation fails"""

    pass


class SQLValidationError(CR360Exception):
    """Raised when SQL validation fails"""

    pass


class SQLExecutionError(DatabaseError):
    """Raised when SQL execution fails"""

    pass


class ContextLoadError(CR360Exception):
    """Raised when context/semantic model loading fails"""

    pass


class AmbiguousQueryError(CR360Exception):
    """Raised when user query is ambiguous"""

    def __init__(self, message: str, options: list = None, questions: list = None):
        super().__init__(message)
        self.options = options or []
        self.questions = questions or []
