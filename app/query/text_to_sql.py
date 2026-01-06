"""
Text-to-SQL Engine for CR360

Implements 4-step process:
1. Natural Language Understanding - Parse user intent
2. Semantic Mapping - Map to metrics/dimensions
3. Query Generation - Generate SQL using LLM
4. Validation & Execution - Validate and execute SQL
"""

import sqlparse
from typing import Dict, Any, List, Optional
from app.llm.context_loader import get_context_loader
from app.llm.gemini_client import get_gemini_client
from app.database.client import get_database_client
from app.utils.logger import get_logger
from app.utils.exceptions import (
    SQLGenerationError,
    SQLValidationError,
    SQLExecutionError,
    AmbiguousQueryError
)

logger = get_logger(__name__)


class TextToSQLEngine:
    """Converts natural language queries to SQL and executes them"""

    def __init__(self):
        """Initialize the Text-to-SQL engine"""
        self.context_loader = get_context_loader()
        self.llm_client = get_gemini_client()
        self.db_client = get_database_client()

        # Load semantic model
        self.semantic_context = self.context_loader.get_context_for_llm()

        logger.info("text_to_sql_engine_initialized")

    async def process_query(
        self,
        natural_language_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        check_ambiguity: bool = True
    ) -> Dict[str, Any]:
        """
        Process a natural language query through the full pipeline

        Args:
            natural_language_query: User's natural language query
            conversation_history: Optional conversation history
            check_ambiguity: Whether to check for ambiguity first

        Returns:
            Dict containing:
                - sql: Generated SQL query
                - explanation: Plain English explanation
                - results: Query results
                - metrics_used: List of metrics used
                - visualization_hint: Suggested chart type

        Raises:
            AmbiguousQueryError: If query is ambiguous
            SQLGenerationError: If SQL generation fails
            SQLValidationError: If SQL validation fails
            SQLExecutionError: If SQL execution fails
        """
        try:
            logger.info(
                "processing_nl_query",
                query=natural_language_query,
                has_history=conversation_history is not None
            )

            # Step 1: Natural Language Understanding & Ambiguity Detection
            if check_ambiguity:
                ambiguity_result = await self._check_ambiguity(natural_language_query)
                if ambiguity_result['is_ambiguous']:
                    logger.warning(
                        "ambiguous_query_detected",
                        reasons=ambiguity_result['reasons'],
                        questions_count=len(ambiguity_result.get('questions', []))
                    )
                    raise AmbiguousQueryError(
                        message="Your query is ambiguous. Please clarify.",
                        options=ambiguity_result['suggestions'],
                        questions=ambiguity_result.get('questions', [])
                    )

            # Step 2 & 3: Semantic Mapping + Query Generation
            sql_result = await self._generate_sql(
                natural_language_query,
                conversation_history
            )

            # Step 4: Validation
            validation_result = self._validate_sql(sql_result['sql'])
            if not validation_result['is_valid']:
                logger.error(
                    "sql_validation_failed",
                    errors=validation_result['errors']
                )
                raise SQLValidationError(
                    f"Generated SQL is invalid: {', '.join(validation_result['errors'])}"
                )

            # Step 5: Execution
            results = await self._execute_sql(sql_result['sql'])

            # Step 6: Post-processing
            visualization_hint = self._suggest_visualization(
                sql_result['sql'],
                results
            )

            logger.info(
                "nl_query_processed_successfully",
                rows_returned=len(results),
                visualization=visualization_hint
            )

            return {
                'sql': sql_result['sql'],
                'explanation': sql_result['explanation'],
                'results': results,
                'metrics_used': sql_result['metrics_used'],
                'visualization_hint': visualization_hint
            }

        except (AmbiguousQueryError, SQLGenerationError, SQLValidationError, SQLExecutionError):
            # Re-raise expected errors
            raise
        except Exception as e:
            logger.error("unexpected_error_in_query_processing", error=str(e))
            raise SQLGenerationError(f"Failed to process query: {e}")

    async def _check_ambiguity(self, query: str) -> Dict[str, Any]:
        """
        Step 1: Check if query is ambiguous

        Args:
            query: Natural language query

        Returns:
            Dict with is_ambiguous, reasons, suggestions
        """
        logger.info("checking_query_ambiguity")
        return await self.llm_client.detect_ambiguity(
            query,
            self.semantic_context
        )

    async def _generate_sql(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Steps 2 & 3: Semantic mapping and SQL generation

        Args:
            query: Natural language query
            conversation_history: Optional conversation history

        Returns:
            Dict with sql, explanation, metrics_used
        """
        logger.info("generating_sql_from_nl")
        return await self.llm_client.generate_sql(
            query,
            self.semantic_context,
            conversation_history
        )

    def _validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Step 4: Validate generated SQL

        Args:
            sql: SQL query string

        Returns:
            Dict with is_valid and errors list
        """
        logger.info("validating_sql")
        errors = []

        try:
            # Parse SQL
            parsed = sqlparse.parse(sql)

            if not parsed:
                errors.append("Failed to parse SQL")
                return {'is_valid': False, 'errors': errors}

            # Check for basic SQL injection patterns (safety check)
            dangerous_keywords = [
                'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
                'INSERT', 'UPDATE', 'GRANT', 'REVOKE'
            ]

            sql_upper = sql.upper()
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    errors.append(f"Dangerous keyword detected: {keyword}")

            # Check for required SELECT
            if not sql_upper.strip().startswith('SELECT'):
                errors.append("Query must be a SELECT statement")

            # Basic syntax validation using sqlparse
            formatted = sqlparse.format(sql, reindent=True, keyword_case='upper')
            if not formatted:
                errors.append("SQL formatting failed - likely syntax error")

            is_valid = len(errors) == 0

            logger.info(
                "sql_validation_complete",
                is_valid=is_valid,
                errors_count=len(errors)
            )

            return {
                'is_valid': is_valid,
                'errors': errors
            }

        except Exception as e:
            logger.error("sql_validation_error", error=str(e))
            return {
                'is_valid': False,
                'errors': [f"Validation error: {str(e)}"]
            }

    async def _execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """
        Step 5: Execute validated SQL

        Args:
            sql: Validated SQL query

        Returns:
            Query results as list of dicts
        """
        logger.info("executing_sql")
        return await self.db_client.execute_query(sql)

    def _suggest_visualization(
        self,
        sql: str,
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Suggest visualization type based on query and results

        Args:
            sql: SQL query
            results: Query results

        Returns:
            Suggested visualization type (bar, line, table, etc.)
        """
        if not results:
            return 'table'

        # Count columns
        num_columns = len(results[0].keys()) if results else 0
        num_rows = len(results)

        # Simple heuristics for visualization
        sql_lower = sql.lower()

        # Time series detection
        if any(time_word in sql_lower for time_word in ['date', 'month', 'year', 'quarter']):
            if num_rows > 1:
                return 'line'

        # Comparison detection
        if any(comp_word in sql_lower for comp_word in ['region', 'product', 'segment']):
            if num_rows <= 10:
                return 'bar'
            elif num_rows <= 50:
                return 'horizontal_bar'

        # Aggregation detection
        if any(agg in sql_lower for agg in ['sum(', 'avg(', 'count(']):
            if num_rows <= 10:
                return 'bar'

        # Default to table for large result sets or many columns
        if num_rows > 50 or num_columns > 5:
            return 'table'

        # Default
        return 'bar'


# Global singleton instance
_text_to_sql_engine: Optional[TextToSQLEngine] = None


def get_text_to_sql_engine() -> TextToSQLEngine:
    """
    Get the global Text-to-SQL engine instance (singleton pattern)

    Returns:
        TextToSQLEngine instance
    """
    global _text_to_sql_engine
    if _text_to_sql_engine is None:
        _text_to_sql_engine = TextToSQLEngine()
    return _text_to_sql_engine
