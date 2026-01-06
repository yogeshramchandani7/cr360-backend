"""
Unit Tests for Database Client (app/database/client.py)

Tests database operations, connection management, and error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import psycopg2
from app.database.client import DatabaseClient, get_database_client
from app.utils.exceptions import DatabaseError, SQLExecutionError


class TestDatabaseClientInitialization:
    """Test DatabaseClient initialization"""

    def test_database_client_initialization_with_params(self):
        """Test DatabaseClient initializes with provided parameters"""
        client = DatabaseClient(
            supabase_url="https://custom.supabase.co",
            supabase_key="custom_key_123",
            database_url="postgresql://custom:pass@localhost/db"
        )

        assert client.supabase_url == "https://custom.supabase.co"
        assert client.supabase_key == "custom_key_123"
        assert client.database_url == "postgresql://custom:pass@localhost/db"
        assert client._supabase_client is None  # Lazy initialization
        assert client._pg_connection is None  # Lazy initialization

    @patch('app.database.client.settings')
    def test_database_client_initialization_defaults(self, mock_settings):
        """Test DatabaseClient uses settings defaults"""
        mock_settings.SUPABASE_URL = "https://settings.supabase.co"
        mock_settings.SUPABASE_KEY = "settings_key"
        mock_settings.DATABASE_URL = "postgresql://settings:pass@localhost/db"

        client = DatabaseClient()

        assert client.supabase_url == "https://settings.supabase.co"
        assert client.supabase_key == "settings_key"
        assert client.database_url == "postgresql://settings:pass@localhost/db"


class TestSupabaseClientProperty:
    """Test Supabase client property (lazy initialization)"""

    @patch('app.database.client.create_client')
    def test_supabase_property_lazy_initialization(self, mock_create_client):
        """Test that Supabase client is created on first access"""
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        client = DatabaseClient(
            supabase_url="https://test.supabase.co",
            supabase_key="test_key"
        )

        # First access should create client
        supabase = client.supabase

        mock_create_client.assert_called_once_with(
            "https://test.supabase.co",
            "test_key"
        )
        assert supabase is mock_supabase

    @patch('app.database.client.create_client')
    def test_supabase_property_cached(self, mock_create_client):
        """Test that Supabase client is cached after first access"""
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        client = DatabaseClient(
            supabase_url="https://test.supabase.co",
            supabase_key="test_key"
        )

        # Access twice
        supabase1 = client.supabase
        supabase2 = client.supabase

        # Should only create once
        assert mock_create_client.call_count == 1
        assert supabase1 is supabase2


class TestPostgreSQLConnection:
    """Test PostgreSQL connection management"""

    @patch('app.database.client.psycopg2.connect')
    def test_get_pg_connection_success(self, mock_connect):
        """Test successful PostgreSQL connection"""
        mock_conn = Mock()
        mock_conn.closed = False
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        conn = client.get_pg_connection()

        mock_connect.assert_called_once()
        assert conn is mock_conn

    @patch('app.database.client.psycopg2.connect')
    def test_get_pg_connection_cached(self, mock_connect):
        """Test that PostgreSQL connection is cached"""
        mock_conn = Mock()
        mock_conn.closed = False
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        # Get connection twice
        conn1 = client.get_pg_connection()
        conn2 = client.get_pg_connection()

        # Should only connect once
        assert mock_connect.call_count == 1
        assert conn1 is conn2

    @patch('app.database.client.psycopg2.connect')
    def test_get_pg_connection_reconnects_if_closed(self, mock_connect):
        """Test that connection is recreated if closed"""
        # First connection (closed)
        mock_conn1 = Mock()
        mock_conn1.closed = True

        # Second connection (open)
        mock_conn2 = Mock()
        mock_conn2.closed = False

        mock_connect.side_effect = [mock_conn1, mock_conn2]

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        # First call
        conn1 = client.get_pg_connection()
        # Manually set connection
        client._pg_connection = mock_conn1

        # Second call should reconnect since connection is closed
        conn2 = client.get_pg_connection()

        assert mock_connect.call_count == 2

    @patch('app.database.client.psycopg2.connect')
    def test_get_pg_connection_failure(self, mock_connect):
        """Test PostgreSQL connection failure"""
        mock_connect.side_effect = psycopg2.Error("Connection refused")

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        with pytest.raises(DatabaseError) as exc_info:
            client.get_pg_connection()

        assert "Failed to connect to PostgreSQL" in str(exc_info.value)


class TestExecuteQuery:
    """Test execute_query method"""

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_execute_query_select_success(self, mock_connect):
        """Test successful SELECT query execution"""
        # Mock cursor
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'Test1'},
            {'id': 2, 'name': 'Test2'}
        ]

        # Mock connection
        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        results = await client.execute_query("SELECT * FROM test_table")

        assert len(results) == 2
        assert results[0]['id'] == 1
        assert results[1]['name'] == 'Test2'
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table", None)
        mock_cursor.close.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_execute_query_with_params(self, mock_connect):
        """Test query execution with parameters"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{'count': 10}]

        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        results = await client.execute_query(
            "SELECT COUNT(*) as count FROM table WHERE id = %s",
            params=(123,)
        )

        assert len(results) == 1
        assert results[0]['count'] == 10
        mock_cursor.execute.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_execute_query_empty_results(self, mock_connect):
        """Test query with empty result set"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []

        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        results = await client.execute_query("SELECT * FROM empty_table")

        assert results == []
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_execute_query_sql_error(self, mock_connect):
        """Test handling of SQL execution errors"""
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = psycopg2.Error("Syntax error")

        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.rollback = Mock()
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        with pytest.raises(SQLExecutionError) as exc_info:
            await client.execute_query("SELECT * FROM nonexistent_table")

        assert "SQL execution failed" in str(exc_info.value)
        mock_conn.rollback.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_execute_query_non_select_statement(self, mock_connect):
        """Test execution of non-SELECT queries (INSERT, UPDATE, etc.)"""
        mock_cursor = Mock()

        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.commit = Mock()
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        results = await client.execute_query("INSERT INTO table VALUES (1, 'test')")

        assert results == []
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_execute_query_unexpected_error(self, mock_connect):
        """Test handling of unexpected errors"""
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Unexpected error")

        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        with pytest.raises(DatabaseError) as exc_info:
            await client.execute_query("SELECT * FROM table")

        assert "Database operation failed" in str(exc_info.value)


class TestQueryTable:
    """Test query_table method (Supabase REST API)"""

    @pytest.mark.asyncio
    @patch('app.database.client.create_client')
    async def test_query_table_success(self, mock_create_client):
        """Test successful table query using Supabase"""
        # Mock response
        mock_response = Mock()
        mock_response.data = [
            {'id': 1, 'name': 'Row1'},
            {'id': 2, 'name': 'Row2'}
        ]

        # Mock query chain
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = mock_response

        # Mock table
        mock_table = Mock()
        mock_table.return_value = mock_query

        # Mock Supabase client
        mock_supabase = Mock()
        mock_supabase.table.return_value = mock_query
        mock_create_client.return_value = mock_supabase

        client = DatabaseClient(
            supabase_url="https://test.supabase.co",
            supabase_key="test_key"
        )

        results = await client.query_table(
            table_name="test_table",
            limit=100
        )

        assert len(results) == 2
        assert results[0]['id'] == 1
        mock_supabase.table.assert_called_once_with("test_table")

    @pytest.mark.asyncio
    @patch('app.database.client.create_client')
    async def test_query_table_with_columns(self, mock_create_client):
        """Test table query with specific columns"""
        mock_response = Mock()
        mock_response.data = [{'id': 1}, {'id': 2}]

        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_supabase = Mock()
        mock_supabase.table.return_value = mock_query
        mock_create_client.return_value = mock_supabase

        client = DatabaseClient(
            supabase_url="https://test.supabase.co",
            supabase_key="test_key"
        )

        results = await client.query_table(
            table_name="test_table",
            columns=["id", "name"],
            limit=50
        )

        mock_query.select.assert_called_once_with("id,name")

    @pytest.mark.asyncio
    @patch('app.database.client.create_client')
    async def test_query_table_with_filters(self, mock_create_client):
        """Test table query with filters"""
        mock_response = Mock()
        mock_response.data = [{'id': 1, 'status': 'active'}]

        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = mock_response

        mock_supabase = Mock()
        mock_supabase.table.return_value = mock_query
        mock_create_client.return_value = mock_supabase

        client = DatabaseClient(
            supabase_url="https://test.supabase.co",
            supabase_key="test_key"
        )

        results = await client.query_table(
            table_name="test_table",
            filters={'status': 'active', 'region': 'US'},
            limit=100
        )

        # eq should be called for each filter
        assert mock_query.eq.call_count == 2

    @pytest.mark.asyncio
    @patch('app.database.client.create_client')
    async def test_query_table_error(self, mock_create_client):
        """Test table query error handling"""
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.side_effect = Exception("API Error")

        mock_supabase = Mock()
        mock_supabase.table.return_value = mock_query
        mock_create_client.return_value = mock_supabase

        client = DatabaseClient(
            supabase_url="https://test.supabase.co",
            supabase_key="test_key"
        )

        with pytest.raises(DatabaseError) as exc_info:
            await client.query_table(table_name="test_table")

        assert "Failed to query table" in str(exc_info.value)


class TestConnectionTesting:
    """Test test_connection method"""

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_test_connection_success(self, mock_connect):
        """Test successful connection test"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{'test': 1}]

        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        result = await client.test_connection()

        assert result is True

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_test_connection_failure(self, mock_connect):
        """Test connection test failure"""
        mock_connect.side_effect = psycopg2.Error("Connection refused")

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        with pytest.raises(DatabaseError) as exc_info:
            await client.test_connection()

        assert "Database connection test failed" in str(exc_info.value)


class TestConnectionManagement:
    """Test connection management methods"""

    @patch('app.database.client.psycopg2.connect')
    def test_close_connection(self, mock_connect):
        """Test closing PostgreSQL connection"""
        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.close = Mock()
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        # Establish connection
        client.get_pg_connection()

        # Close connection
        client.close()

        mock_conn.close.assert_called_once()

    def test_close_connection_when_not_established(self):
        """Test closing connection when no connection exists"""
        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        # Should not raise error
        client.close()

    @patch('app.database.client.psycopg2.connect')
    def test_close_connection_already_closed(self, mock_connect):
        """Test closing connection that is already closed"""
        mock_conn = Mock()
        mock_conn.closed = True
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")
        client._pg_connection = mock_conn

        # Should not attempt to close
        client.close()


class TestSingletonPattern:
    """Test get_database_client singleton pattern"""

    def test_get_database_client_returns_instance(self):
        """Test that get_database_client returns a DatabaseClient instance"""
        # Reset singleton
        import app.database.client as db_module
        db_module._database_client = None

        client = get_database_client()
        assert isinstance(client, DatabaseClient)

        # Clean up
        db_module._database_client = None

    def test_get_database_client_returns_same_instance(self):
        """Test that get_database_client returns the same instance (singleton)"""
        # Reset singleton
        import app.database.client as db_module
        db_module._database_client = None

        client1 = get_database_client()
        client2 = get_database_client()

        assert client1 is client2

        # Clean up
        db_module._database_client = None


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_execute_query_very_long_sql(self, mock_connect):
        """Test execution of very long SQL query"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{'result': 1}]

        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        long_sql = "SELECT * FROM table WHERE " + " OR ".join([f"id = {i}" for i in range(1000)])

        results = await client.execute_query(long_sql)
        assert len(results) == 1

    @pytest.mark.asyncio
    @patch('app.database.client.psycopg2.connect')
    async def test_execute_query_special_characters(self, mock_connect):
        """Test query with special characters"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{'name': "Test's Name"}]

        mock_conn = Mock()
        mock_conn.closed = False
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = DatabaseClient(database_url="postgresql://test:pass@localhost/db")

        results = await client.execute_query(
            "SELECT * FROM table WHERE name = %s",
            params=("Test's Name",)
        )

        assert len(results) == 1
