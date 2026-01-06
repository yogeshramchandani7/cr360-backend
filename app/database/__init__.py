"""Database module for CR360"""

from app.database.client import DatabaseClient, get_database_client

__all__ = ['DatabaseClient', 'get_database_client']
