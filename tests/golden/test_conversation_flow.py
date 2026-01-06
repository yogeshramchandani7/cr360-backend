"""
Golden Tests for Conversation Flow

End-to-end tests for multi-turn conversation scenarios
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestConversationFlows:
    """Golden tests for multi-turn conversations"""

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_conversation_single_turn(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: Single Q&A turn"""
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
            'sql': 'SELECT SUM(balance) FROM table',
            'explanation': 'Total balance',
            'metrics_used': ['total_exposure']
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[{'total': 2800000000}])
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()

        result = await engine.process_query(
            natural_language_query="What is total exposure?",
            conversation_history=None,
            check_ambiguity=True
        )

        assert result['results'][0]['total'] == 2800000000

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_conversation_follow_up(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: Question → Follow-up question"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        # First turn
        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT SUM(balance) as total FROM table',
            'explanation': 'Total exposure',
            'metrics_used': ['total_exposure']
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[{'total': 2800000000}])
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()

        # First query
        result1 = await engine.process_query(
            natural_language_query="What is total exposure?",
            conversation_history=None,
            check_ambiguity=True
        )

        # Second turn (follow-up)
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT product_name, SUM(balance) as total FROM table GROUP BY product_name',
            'explanation': 'Exposure by product',
            'metrics_used': ['total_exposure']
        })

        mock_db.execute_query = AsyncMock(return_value=[
            {'product_name': 'Mortgage', 'total': 1500000000},
            {'product_name': 'Auto Loan', 'total': 800000000},
            {'product_name': 'Credit Card', 'total': 500000000}
        ])

        conversation_history = [
            {'user': 'What is total exposure?', 'assistant': 'Total is $2.8B'}
        ]

        result2 = await engine.process_query(
            natural_language_query="Show me by product",
            conversation_history=conversation_history,
            check_ambiguity=True
        )

        assert len(result2['results']) == 3
        assert all('product_name' in row for row in result2['results'])

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_conversation_clarification(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: Ambiguous → Clarification → Success"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        # Setup database mock BEFORE creating engine
        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[{'total': 2800000000}])
        mock_get_db.return_value = mock_db

        # First turn - ambiguous
        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': True,
            'reasons': ['Missing time period'],
            'suggestions': ['Specify a time period']
        })
        mock_get_llm.return_value = mock_llm

        from app.query.text_to_sql import get_text_to_sql_engine
        from app.utils.exceptions import AmbiguousQueryError
        engine = get_text_to_sql_engine()

        # First attempt fails
        with pytest.raises(AmbiguousQueryError) as exc_info:
            await engine.process_query(
                natural_language_query="Show me the metrics",
                conversation_history=None,
                check_ambiguity=True
            )

        assert len(exc_info.value.options) > 0

        # Second turn - clarified
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT SUM(balance) FROM table WHERE date = CURRENT_DATE',
            'explanation': 'Metrics as of today',
            'metrics_used': ['total_exposure']
        })

        # Database mock already setup above, no need to recreate

        conversation_history = [
            {'user': 'Show me the metrics', 'assistant': 'Please specify time period'},
            {'user': 'For today', 'assistant': ''}
        ]

        result = await engine.process_query(
            natural_language_query="Show me the metrics for today",
            conversation_history=conversation_history,
            check_ambiguity=True
        )

        assert result['results'] is not None

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_conversation_context_maintained(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: Context preserved across turns"""
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
            'sql': 'SELECT * FROM table',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[])
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()

        conversation_history = [
            {'user': 'What is total exposure?', 'assistant': '$2.8B'},
            {'user': 'Show by product', 'assistant': 'Mortgage $1.5B, Auto $800M, CC $500M'}
        ]

        # Third turn should have access to history
        result = await engine.process_query(
            natural_language_query="What about regions?",
            conversation_history=conversation_history,
            check_ambiguity=True
        )

        # Verify generate_sql was called with history
        mock_llm.generate_sql.assert_called_once()
        call_args = mock_llm.generate_sql.call_args
        # generate_sql is called with (query, semantic_context, conversation_history)
        # Check positional arg [2] (index 0 is self, 1 is query, 2 is semantic_context, 3 is conversation_history)
        # In call_args, [0] is positional args tuple, so [0][2] is the 3rd positional arg
        assert call_args[0][2] == conversation_history

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_conversation_id_consistency(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db,
        test_client
    ):
        """Golden: Same conversation_id used across turns"""
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
            'sql': 'SELECT 1',
            'explanation': 'Test',
            'metrics_used': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_db.execute_query = AsyncMock(return_value=[])
        mock_get_db.return_value = mock_db

        conversation_id = "test-conversation-123"

        # First request
        response1 = test_client.post(
            "/api/v1/chat",
            json={
                "query": "What is total exposure?",
                "conversation_id": conversation_id
            }
        )

        # Second request with same conversation_id
        response2 = test_client.post(
            "/api/v1/chat",
            json={
                "query": "Show by product",
                "conversation_id": conversation_id,
                "conversation_history": [
                    {"role": "user", "content": "What is total exposure?"},
                    {"role": "assistant", "content": "$2.8B"}
                ]
            }
        )

        assert response1.json()['conversation_id'] == conversation_id
        assert response2.json()['conversation_id'] == conversation_id


class TestComplexScenarios:
    """Golden tests for complex conversation scenarios"""

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_drill_down_sequence(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: Total → By Product → By Region"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()

        # Turn 1: Total
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT SUM(balance) FROM table',
            'explanation': 'Total',
            'metrics_used': ['total_exposure']
        })
        mock_db.execute_query = AsyncMock(return_value=[{'total': 2800000000}])

        result1 = await engine.process_query(
            natural_language_query="What is total exposure?",
            conversation_history=None
        )

        # Turn 2: By Product
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT product_name, SUM(balance) FROM table GROUP BY product_name',
            'explanation': 'By product',
            'metrics_used': ['total_exposure']
        })
        mock_db.execute_query = AsyncMock(return_value=[
            {'product_name': 'Mortgage', 'total': 1500000000}
        ])

        result2 = await engine.process_query(
            natural_language_query="Show by product",
            conversation_history=[{'user': 'What is total exposure?', 'assistant': '$2.8B'}]
        )

        # Turn 3: By Region
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT region_name, SUM(balance) FROM table GROUP BY region_name',
            'explanation': 'By region',
            'metrics_used': ['total_exposure']
        })
        mock_db.execute_query = AsyncMock(return_value=[
            {'region_name': 'Northeast', 'total': 700000000}
        ])

        result3 = await engine.process_query(
            natural_language_query="Now show by region",
            conversation_history=[
                {'user': 'What is total exposure?', 'assistant': '$2.8B'},
                {'user': 'Show by product', 'assistant': 'Mortgage $1.5B'}
            ]
        )

        assert result1 is not None
        assert result2 is not None
        assert result3 is not None

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_refinement_sequence(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: Broad query → Refined query"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()

        # Broad query
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT * FROM table LIMIT 1000',
            'explanation': 'All data',
            'metrics_used': []
        })
        mock_db.execute_query = AsyncMock(return_value=[{'count': 1000}])

        result1 = await engine.process_query(
            natural_language_query="Show me all the data",
            conversation_history=None
        )

        # Refined query
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT * FROM table WHERE product = \'Mortgage\' LIMIT 100',
            'explanation': 'Mortgage data only',
            'metrics_used': []
        })
        mock_db.execute_query = AsyncMock(return_value=[{'count': 100}])

        result2 = await engine.process_query(
            natural_language_query="Just for Mortgage products",
            conversation_history=[
                {'user': 'Show me all the data', 'assistant': '1000 rows returned'}
            ]
        )

        assert result1 is not None
        assert result2 is not None

    @pytest.mark.asyncio
    @patch('app.query.text_to_sql.get_database_client')
    @patch('app.query.text_to_sql.get_gemini_client')
    @patch('app.query.text_to_sql.get_context_loader')
    async def test_golden_error_recovery(
        self,
        mock_get_context,
        mock_get_llm,
        mock_get_db
    ):
        """Golden: Error → Successful retry"""
        mock_context_loader = Mock()
        mock_context_loader.get_context_for_llm.return_value = "YAML context"
        mock_get_context.return_value = mock_context_loader

        mock_llm = Mock()
        mock_llm.detect_ambiguity = AsyncMock(return_value={
            'is_ambiguous': False,
            'reasons': [],
            'suggestions': []
        })
        mock_get_llm.return_value = mock_llm

        mock_db = Mock()
        mock_get_db.return_value = mock_db

        from app.query.text_to_sql import get_text_to_sql_engine
        engine = get_text_to_sql_engine()

        # First attempt fails
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT * FROM nonexistent_table',
            'explanation': 'Error query',
            'metrics_used': []
        })
        mock_db.execute_query = AsyncMock(side_effect=Exception("Table not found"))

        with pytest.raises(Exception):
            await engine.process_query(
                natural_language_query="Show me the data",
                conversation_history=None
            )

        # Retry succeeds
        mock_llm.generate_sql = AsyncMock(return_value={
            'sql': 'SELECT * FROM correct_table',
            'explanation': 'Correct query',
            'metrics_used': []
        })
        mock_db.execute_query = AsyncMock(return_value=[{'count': 100}])

        result = await engine.process_query(
            natural_language_query="Show me the data from the correct table",
            conversation_history=[
                {'user': 'Show me the data', 'assistant': 'Error: table not found'}
            ]
        )

        assert result is not None
        assert len(result['results']) > 0
