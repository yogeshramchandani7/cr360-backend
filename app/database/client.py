"""
Database Client for CR360

Handles all database operations with connection pooling and error handling
"""

from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import DatabaseError, SQLExecutionError

logger = get_logger(__name__)


class DatabaseClient:
    """Database client for Supabase/PostgreSQL operations"""

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        database_url: Optional[str] = None
    ):
        """
        Initialize database client

        Args:
            supabase_url: Supabase URL (defaults to settings.SUPABASE_URL)
            supabase_key: Supabase API key (defaults to settings.SUPABASE_KEY)
            database_url: PostgreSQL connection URL (defaults to settings.DATABASE_URL)
        """
        self.supabase_url = supabase_url or settings.SUPABASE_URL
        self.supabase_key = supabase_key or settings.SUPABASE_KEY
        self.database_url = database_url or settings.DATABASE_URL

        self._supabase_client: Optional[Client] = None
        self._pg_connection = None

        logger.info("database_client_initialized")

    @property
    def supabase(self) -> Client:
        """Get Supabase client (lazy initialization)"""
        if self._supabase_client is None:
            self._supabase_client = create_client(self.supabase_url, self.supabase_key)
            logger.info("supabase_client_created")
        return self._supabase_client

    def get_pg_connection(self):
        """Get PostgreSQL connection (lazy initialization)"""
        if self._pg_connection is None or self._pg_connection.closed:
            try:
                self._pg_connection = psycopg2.connect(
                    self.database_url,
                    cursor_factory=RealDictCursor
                )
                logger.info("postgresql_connection_established")
            except Exception as e:
                logger.error("postgresql_connection_error", error=str(e))
                raise DatabaseError(f"Failed to connect to PostgreSQL: {e}")
        return self._pg_connection

    async def execute_query(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results

        Args:
            sql: SQL query string
            params: Optional query parameters for safe parameterization

        Returns:
            List of result rows as dictionaries

        Raises:
            SQLExecutionError: If query execution fails
        """
        try:
            logger.info(
                "executing_sql_query",
                sql_preview=sql[:200]
            )

            conn = self.get_pg_connection()
            cursor = conn.cursor()

            # Execute query
            cursor.execute(sql, params)

            # Fetch results if it's a SELECT query
            if sql.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                # Convert to list of dicts
                results_list = [dict(row) for row in results]
            else:
                # For non-SELECT queries, commit and return empty list
                conn.commit()
                results_list = []

            cursor.close()

            logger.info(
                "sql_query_executed",
                rows_returned=len(results_list)
            )

            return results_list

        except psycopg2.Error as e:
            logger.error("sql_execution_error", error=str(e), sql=sql[:200])
            # Rollback on error
            if self._pg_connection and not self._pg_connection.closed:
                self._pg_connection.rollback()
            raise SQLExecutionError(f"SQL execution failed: {e}")
        except Exception as e:
            logger.error("unexpected_database_error", error=str(e))
            raise DatabaseError(f"Database operation failed: {e}")

    async def query_table(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query a table using Supabase REST API

        Args:
            table_name: Name of the table
            columns: List of columns to select (defaults to all)
            filters: Dictionary of column:value filters
            limit: Maximum rows to return

        Returns:
            List of result rows

        Raises:
            DatabaseError: If query fails
        """
        try:
            logger.info(
                "querying_table",
                table=table_name,
                filters=filters,
                limit=limit
            )

            query = self.supabase.table(table_name)

            # Select columns
            if columns:
                query = query.select(','.join(columns))
            else:
                query = query.select('*')

            # Apply filters
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            # Apply limit
            query = query.limit(limit)

            # Execute
            response = query.execute()

            logger.info(
                "table_query_executed",
                rows_returned=len(response.data)
            )

            return response.data

        except Exception as e:
            logger.error("table_query_error", error=str(e), table=table_name)
            raise DatabaseError(f"Failed to query table {table_name}: {e}")

    async def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            True if connection successful

        Raises:
            DatabaseError: If connection fails
        """
        try:
            result = await self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except Exception as e:
            logger.error("connection_test_failed", error=str(e))
            raise DatabaseError(f"Database connection test failed: {e}")

    def close(self):
        """Close database connections"""
        if self._pg_connection and not self._pg_connection.closed:
            self._pg_connection.close()
            logger.info("postgresql_connection_closed")


# Global singleton instance
_database_client: Optional[DatabaseClient] = None


def get_database_client() -> DatabaseClient:
    """
    Get the global database client instance (singleton pattern)

    Returns:
        DatabaseClient instance
    """
    global _database_client
    if _database_client is None:
        _database_client = DatabaseClient()
    return _database_client
