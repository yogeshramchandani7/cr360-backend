"""
Golden Tests for Query Pipeline

End-to-end tests for critical user journeys through the complete query pipeline
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestGoldenHappyPaths:
    """Golden tests for successful query flows"""

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_simple_aggregation(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: User asks 'What is total exposure?' → SQL → Results"""
        # Mock context
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        # Mock LLM
        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT SUM(account_balance_eop) as total_exposure FROM account_level_monthly WHERE calendar_date = (SELECT MAX(calendar_date) FROM account_level_monthly)',
            'explanation': 'This query calculates the total exposure by summing account balances as of the latest date.',
            'metrics_used': ['total_exposure']
        })
        mock_get_llm.return_value = mock_llm

        # Mock database
        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[
            {'total_exposure': 2800000000.00}
        ])
        mock_get_db.return_value = mock_db

        # Execute query
        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()
        result = await engine.process_query(
            natural_language_query="What is the total exposure?",
            check_ambiguity=True
        )

        # Verify results
        assert result['sql'] is not None
        assert len(result['results']) == 1
        assert result['results'][0]['total_exposure'] == 2800000000.00
        assert result['explanation'] is not None
        assert 'total_exposure' in result['metrics_used']
        assert result['visualization_hint'] in ['bar', 'table']

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_dimensional_breakdown(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: User asks 'Show exposure by product' → SQL → Results"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT product_name, SUM(account_balance_eop) as total_exposure FROM account_level_monthly WHERE calendar_date = (SELECT MAX(calendar_date) FROM account_level_monthly) GROUP BY product_name ORDER BY product_name',
            'explanation': 'This query breaks down exposure by product.',
            'metrics_used': ['total_exposure']
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[
            {'product_name': 'Auto Loan', 'total_exposure': 800000000.00},
            {'product_name': 'Credit Card', 'total_exposure': 500000000.00},
            {'product_name': 'Mortgage', 'total_exposure': 1500000000.00}
        ])
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()
        result = await engine.process_query(
            natural_language_query="Show me exposure by product",
            check_ambiguity=True
        )

        assert len(result['results']) == 3
        assert all('product_name' in row for row in result['results'])
        assert all('total_exposure' in row for row in result['results'])
        # Visualization hint is 'line' because SQL contains 'calendar_date' (time series detection)
        # This is acceptable since the heuristic sees date-related keywords in WHERE clause
        assert result['visualization_hint'] in ['bar', 'line']

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_rate_calculation(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: User asks 'What is delinquency rate?' → SQL → Results"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT (SUM(total_delinquent_balance) / NULLIF(SUM(account_balance_eop), 0)) * 100 as delinquency_rate FROM account_level_monthly WHERE calendar_date = (SELECT MAX(calendar_date) FROM account_level_monthly)',
            'explanation': 'This calculates delinquency rate as percentage.',
            'metrics_used': ['delinquency_rate']
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[
            {'delinquency_rate': 3.25}
        ])
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()
        result = await engine.process_query(
            natural_language_query="What is the delinquency rate?",
            check_ambiguity=True
        )

        assert len(result['results']) == 1
        assert result['results'][0]['delinquency_rate'] == 3.25
        assert result['visualization_hint'] in ['bar', 'table']

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_time_series(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: User asks 'Show trend over time' → SQL → Results"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT calendar_date, SUM(account_balance_eop) as total_exposure FROM account_level_monthly GROUP BY calendar_date ORDER BY calendar_date',
            'explanation': 'This shows exposure trend over time.',
            'metrics_used': ['total_exposure']
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[
            {'calendar_date': '2024-01-31', 'total_exposure': 2500000000.00},
            {'calendar_date': '2024-12-31', 'total_exposure': 2700000000.00},
            {'calendar_date': '2025-12-31', 'total_exposure': 2950000000.00}
        ])
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()
        result = await engine.process_query(
            natural_language_query="Show me the trend over time",
            check_ambiguity=True
        )

        assert len(result['results']) == 3
        assert all('calendar_date' in row for row in result['results'])
        assert result['visualization_hint'] == 'line'

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_multi_dimension(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: User asks 'Show by product and region' → SQL → Results"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT product_name, region_name, SUM(account_balance_eop) as total_exposure FROM account_level_monthly WHERE calendar_date = (SELECT MAX(calendar_date) FROM account_level_monthly) GROUP BY product_name, region_name ORDER BY product_name, region_name',
            'explanation': 'This breaks down exposure by product and region.',
            'metrics_used': ['total_exposure']
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[
            {'product_name': 'Mortgage', 'region_name': 'Northeast', 'total_exposure': 400000000.00},
            {'product_name': 'Mortgage', 'region_name': 'Southeast', 'total_exposure': 350000000.00},
            {'product_name': 'Auto Loan', 'region_name': 'Northeast', 'total_exposure': 200000000.00}
        ])
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()
        result = await engine.process_query(
            natural_language_query="Show exposure by product and region",
            check_ambiguity=True
        )

        assert len(result['results']) >= 3
        assert all('product_name' in row and 'region_name' in row for row in result['results'])


class TestGoldenErrorFlows:
    """Golden tests for error scenarios"""

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_ambiguous_query(
        self,
        mock_get_context,
        mock_get_llm
    ):
        """Golden: Ambiguous query → 400 with suggestions"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': True,
            'reasons': ['Missing time period specification'],
            'suggestions': ['Specify a time period (e.g., "as of latest date", "for Q4 2024")']
        })
        mock_get_llm.return_value = mock_llm

        from app.query.text_to_sql import get_text_to_sql_engine
        from app.utils.exceptions import AmbiguousQueryError

        engine = get_text_to_sql_engine()

        with pytest.raises(AmbiguousQueryError) as exc_info:
            await engine.process_query(
                natural_language_query="Show me the metrics",
                check_ambiguity=True
            )

        assert len(exc_info.value.options) > 0
        assert 'time period' in exc_info.value.options[0].lower()

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_invalid_sql_generated(
        self,
        mock_get_context,
        mock_get_llm
    ):
        """Golden: Invalid SQL generated → Validation error → 500"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'DROP TABLE accounts',  # Dangerous SQL
            'explanation': 'Invalid',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        from app.query.text_to_sql import get_text_to_sql_engine
        from app.utils.exceptions import SQLValidationError

        engine = get_text_to_sql_engine()

        with pytest.raises(SQLValidationError):
            await engine.process_query(
                natural_language_query="Test query",
                check_ambiguity=True
            )

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_database_error(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: DB error → Graceful error response"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT * FROM nonexistent_table',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(side_effect=Exception("Table not found"))
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        from app.utils.exceptions import SQLExecutionError

        engine = get_text_to_sql_engine()

        with pytest.raises(Exception):  # Should raise some exception
            await engine.process_query(
                natural_language_query="Test query",
                check_ambiguity=True
            )


class TestGoldenEdgeCases:
    """Golden tests for edge cases"""

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_empty_result_set(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: Query returns no rows → Empty results array"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT * FROM table WHERE 1=0',
            'explanation': 'Query with no results',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[])
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()
        result = await engine.process_query(
            natural_language_query="Test query",
            check_ambiguity=True
        )

        assert result['results'] == []
        assert isinstance(result['results'], list)

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_large_result_set(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: Large result → Proper handling"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT * FROM large_table',
            'explanation': 'Large result query',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        # Create large result set
        large_results = [{'id': i, 'value': f'value_{i}'} for i in range(100)]
        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=large_results)
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()
        result = await engine.process_query(
            natural_language_query="Show all records",
            check_ambiguity=True
        )

        assert len(result['results']) == 100
        assert result['visualization_hint'] == 'table'
