"""
Unit Tests for Text-to-SQL Engine (app/query/text_to_sql.py)

Tests the complete Text-to-SQL pipeline with mocked dependencies
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from app.query.text_to_sql import TextToSQLEngine, get_text_to_sql_engine
from app.utils.exceptions import (
    AmbiguousQueryError,
    SQLGenerationError,
    SQLValidationError,
    SQLExecutionError
)


class TestTextToSQLEngineInitialization:
    """Test TextToSQLEngine initialization"""

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_text_to_sql_engine_initialization(
        self,
        mock_get_db,
        mock_get_llm,
        mock_get_context
    ):
        """Test that TextToSQLEngine initializes all dependencies"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm_client = Mock()
        mock_get_llm.return_value = mock_llm_client

        mock_db_client = Mock()
        mock_get_db.return_value = mock_db_client

        engine = TextToSQLEngine()

        assert engine.context_loader is mock_context_loader
        assert engine.llm_client is mock_llm_client
        assert engine.db_client is mock_db_client
        assert engine.semantic_context == "YAML context"


class TestSQLValidation:
    """Test _validate_sql method"""

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_validate_sql_valid_select(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test validation passes for valid SELECT query"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "SELECT product_name, SUM(balance) FROM table GROUP BY product_name"
        result = engine._validate_sql(sql)

        assert result['is_valid'] is True
        assert result['errors'] == []

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_validate_sql_rejects_drop(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test validation rejects DROP statements"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "DROP TABLE accounts"
        result = engine._validate_sql(sql)

        assert result['is_valid'] is False
        assert any('DROP' in error for error in result['errors'])

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_validate_sql_rejects_delete(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test validation rejects DELETE statements"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "DELETE FROM accounts WHERE id = 1"
        result = engine._validate_sql(sql)

        assert result['is_valid'] is False
        assert any('DELETE' in error for error in result['errors'])

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_validate_sql_rejects_truncate(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test validation rejects TRUNCATE statements"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "TRUNCATE TABLE accounts"
        result = engine._validate_sql(sql)

        assert result['is_valid'] is False
        assert any('TRUNCATE' in error for error in result['errors'])

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_validate_sql_rejects_alter(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test validation rejects ALTER statements"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "ALTER TABLE accounts ADD COLUMN new_col INT"
        result = engine._validate_sql(sql)

        assert result['is_valid'] is False
        assert any('ALTER' in error for error in result['errors'])

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_validate_sql_rejects_insert(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test validation rejects INSERT statements"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "INSERT INTO accounts VALUES (1, 'test')"
        result = engine._validate_sql(sql)

        assert result['is_valid'] is False
        assert any('INSERT' in error for error in result['errors'])

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_validate_sql_rejects_update(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test validation rejects UPDATE statements"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "UPDATE accounts SET balance = 0"
        result = engine._validate_sql(sql)

        assert result['is_valid'] is False
        assert any('UPDATE' in error for error in result['errors'])

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_validate_sql_rejects_non_select_start(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test validation rejects non-SELECT queries"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "CREATE TABLE test (id INT)"
        result = engine._validate_sql(sql)

        assert result['is_valid'] is False
        assert any('must be a SELECT statement' in error for error in result['errors'])

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_validate_sql_parse_error(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test handling of SQL parse errors"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = ""  # Empty SQL
        result = engine._validate_sql(sql)

        assert result['is_valid'] is False
        assert len(result['errors']) > 0


class TestVisualizationSuggestion:
    """Test _suggest_visualization method"""

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_suggest_visualization_time_series(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test suggesting line chart for time series data"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "SELECT calendar_date, SUM(balance) FROM table GROUP BY calendar_date ORDER BY calendar_date"
        results = [
            {'calendar_date': '2024-01-01', 'balance': 1000},
            {'calendar_date': '2024-02-01', 'balance': 1100},
            {'calendar_date': '2024-03-01', 'balance': 1200}
        ]

        viz = engine._suggest_visualization(sql, results)

        assert viz == 'line'

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_suggest_visualization_comparison(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test suggesting bar chart for comparisons"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "SELECT region, SUM(balance) FROM table GROUP BY region"
        results = [
            {'region': 'Northeast', 'balance': 1000},
            {'region': 'Southeast', 'balance': 1100},
            {'region': 'Midwest', 'balance': 900}
        ]

        viz = engine._suggest_visualization(sql, results)

        assert viz == 'bar'

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_suggest_visualization_large_dataset(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test suggesting table for large datasets"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "SELECT * FROM large_table"
        results = [{'id': i} for i in range(100)]  # 100 rows

        viz = engine._suggest_visualization(sql, results)

        assert viz == 'table'

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_suggest_visualization_default(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test default visualization suggestion"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "SELECT SUM(balance) FROM table"
        results = [{'sum': 10000}]

        viz = engine._suggest_visualization(sql, results)

        assert viz == 'bar'

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_suggest_visualization_empty_results(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test visualization suggestion for empty results"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = TextToSQLEngine()

        sql = "SELECT * FROM table WHERE 1=0"
        results = []

        viz = engine._suggest_visualization(sql, results)

        assert viz == 'table'


class TestProcessQuery:
    """Test process_query method with mocked dependencies"""

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    async def test_process_query_success(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test complete successful query processing"""
        # Mock context loader
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        # Mock LLM client
        mock_llm_client = Mock()
        mock_llm_client.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm_client.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT SUM(balance) as total FROM table',
            'explanation': 'This calculates total balance',
            'metrics_used': ['total_exposure']
        })
        mock_get_llm.return_value = mock_llm_client

        # Mock database client
        mock_db_client = Mock()
        mock_db_client.execute_query = AsyncMock(return_value=[{'total': 2800000000}])
        mock_get_db.return_value = mock_db_client

        engine = TextToSQLEngine()

        result = await engine.process_query(
            natural_language_query="What is the total exposure?",
            check_ambiguity=True
        )

        assert result['sql'] == 'SELECT SUM(balance) as total FROM table'
        assert result['explanation'] == 'This calculates total balance'
        assert result['results'] == [{'total': 2800000000}]
        assert result['metrics_used'] == ['total_exposure']
        assert 'visualization_hint' in result

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    async def test_process_query_ambiguous(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test handling of ambiguous queries"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm_client = Mock()
        mock_llm_client.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': True,
            'reasons': ['Missing time period'],
            'suggestions': ['Specify a time period']
        })
        mock_get_llm.return_value = mock_llm_client

        engine = TextToSQLEngine()

        with pytest.raises(AmbiguousQueryError) as exc_info:
            await engine.process_query(
                natural_language_query="Show me the metrics",
                check_ambiguity=True
            )

        assert 'ambiguous' in str(exc_info.value).lower()
        assert exc_info.value.options == ['Specify a time period']

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    async def test_process_query_skip_ambiguity_check(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test skipping ambiguity check"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm_client = Mock()
        mock_llm_client.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT 1',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm_client

        mock_db_client = Mock()
        mock_db_client.execute_query = AsyncMock(return_value=[{'result': 1}])
        mock_get_db.return_value = mock_db_client

        engine = TextToSQLEngine()

        result = await engine.process_query(
            natural_language_query="Test query",
            check_ambiguity=False  # Skip ambiguity check
        )

        # Should not call detect_ambiguity
        mock_llm_client.detect_ambiguity.assert_not_called()
        assert result['sql'] == 'SELECT 1'

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    async def test_process_query_sql_generation_error(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test handling of SQL generation failures"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm_client = Mock()
        mock_llm_client.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm_client.generate_sql = AsyncMock(side_effect=Exception("LLM API error"))
        mock_get_llm.return_value = mock_llm_client

        engine = TextToSQLEngine()

        with pytest.raises(SQLGenerationError):
            await engine.process_query(
                natural_language_query="Test query",
                check_ambiguity=True
            )

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    async def test_process_query_validation_error(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test handling of SQL validation failures"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm_client = Mock()
        mock_llm_client.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm_client.generate_sql = AsyncMock(return_value={
            'sql': 'DROP TABLE accounts',  # Invalid SQL
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm_client

        engine = TextToSQLEngine()

        with pytest.raises(SQLValidationError) as exc_info:
            await engine.process_query(
                natural_language_query="Test query",
                check_ambiguity=True
            )

        assert 'invalid' in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    async def test_process_query_execution_error(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test handling of SQL execution failures"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm_client = Mock()
        mock_llm_client.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm_client.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT * FROM nonexistent_table',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm_client

        mock_db_client = Mock()
        mock_db_client.execute_query = AsyncMock(side_effect=SQLExecutionError("Table not found"))
        mock_get_db.return_value = mock_db_client

        engine = TextToSQLEngine()

        with pytest.raises(SQLExecutionError):
            await engine.process_query(
                natural_language_query="Test query",
                check_ambiguity=True
            )

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    async def test_process_query_with_conversation_history(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test processing query with conversation history"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        mock_llm_client = Mock()
        mock_llm_client.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm_client.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT * FROM table',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm_client

        mock_db_client = Mock()
        mock_db_client.execute_query = AsyncMock(return_value=[])
        mock_get_db.return_value = mock_db_client

        conversation_history = [
            {'user': 'What is total exposure?', 'assistant': '$2.8B'},
            {'user': 'Show by product', 'assistant': 'Here is the breakdown...'}
        ]

        engine = TextToSQLEngine()

        result = await engine.process_query(
            natural_language_query="What about regions?",
            conversation_history=conversation_history,
            check_ambiguity=True
        )

        # Verify generate_sql was called with conversation history
        mock_llm_client.generate_sql.assert_called_once()
        call_args = mock_llm_client.generate_sql.call_args

        # Check either kwargs or positional args for conversation_history
        if 'conversation_history' in call_args.kwargs:
            assert call_args.kwargs['conversation_history'] == conversation_history
        else:
            # Check positional args (conversation_history is typically 3rd arg after query and context)
            assert conversation_history in call_args.args


class TestSingletonPattern:
    """Test get_text_to_sql_engine singleton pattern"""

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_get_text_to_sql_engine_returns_instance(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test that get_text_to_sql_engine returns TextToSQLEngine instance"""
        # Reset singleton
        import app.query.text_to_sql as tts_module
        tts_module._text_to_sql_engine = None

        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine = get_text_to_sql_engine()
        assert isinstance(engine, TextToSQLEngine)

        # Clean up
        tts_module._text_to_sql_engine = None

    @patch('app.query.text_to_sql.get_context_loader')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_database_client')
    def test_get_text_to_sql_engine_returns_same_instance(self, mock_get_db, mock_get_llm, mock_get_context):
        """Test that get_text_to_sql_engine returns same instance (singleton)"""
        # Reset singleton
        import app.query.text_to_sql as tts_module
        tts_module._text_to_sql_engine = None

        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "context"
        mock_get_context.return_value = mock_context_loader

        engine1 = get_text_to_sql_engine()
        engine2 = get_text_to_sql_engine()

        assert engine1 is engine2

        # Clean up
        tts_module._text_to_sql_engine = None
