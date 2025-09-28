import logging
import signal
import threading
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from decimal import Decimal
from datetime import datetime, date, time
from django.db import connections
from django.conf import settings
import sqlparse

logger = logging.getLogger(__name__)


class QueryTimeoutException(Exception):
    """Exception raised when query execution times out"""
    pass


class DatabaseService:
    def __init__(self):
        self.timeout = settings.SQL_QUERY_TIMEOUT
        self.max_rows = settings.MAX_RESULT_ROWS

    def _serialize_value(self, value):
        """Convert database values to JSON-serializable types"""
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (datetime, date, time)):
            return value.isoformat()
        elif value is None:
            return None
        else:
            return value

    def execute_safe_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute SQL query with safety constraints
        """
        try:
            # Validate and sanitize query
            if not self._is_safe_query(sql_query):
                raise ValueError("Query contains potentially unsafe operations")

            # Parse and format query
            parsed_query = self._parse_and_format_query(sql_query)

            # Execute with timeout
            result = self._execute_with_timeout(parsed_query)

            return {
                'success': True,
                'data': result['data'],
                'columns': result['columns'],
                'row_count': result['row_count'],
                'query': parsed_query
            }

        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'query': sql_query
            }

    def _is_safe_query(self, sql_query: str) -> bool:
        """
        Validate that the query is safe (read-only)
        """
        # Parse the SQL
        parsed = sqlparse.parse(sql_query)

        if not parsed:
            return False

        # Check each statement
        for statement in parsed:
            # Get the first token that's not a comment or whitespace
            first_token = None
            for token in statement.flatten():
                if token.ttype not in (sqlparse.tokens.Comment.Single,
                                     sqlparse.tokens.Comment.Multiline,
                                     sqlparse.tokens.Whitespace,
                                     sqlparse.tokens.Newline):
                    first_token = token
                    break

            if not first_token:
                continue

            # Only allow SELECT statements and WITH (CTE) statements
            if first_token.ttype is sqlparse.tokens.Keyword.DML:
                if first_token.value.upper() != 'SELECT':
                    return False
            elif first_token.ttype is sqlparse.tokens.Keyword:
                if first_token.value.upper() not in ['SELECT', 'WITH', 'CREATE']:
                    return False
            elif first_token.ttype is sqlparse.tokens.Keyword.CTE:
                if first_token.value.upper() != 'WITH':
                    return False
            else:
                # If first meaningful token isn't a keyword, it's likely not a valid query
                return False

            # Check for dangerous keywords
            dangerous_keywords = [
                'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER',
                'TRUNCATE', 'EXEC', 'EXECUTE', 'CALL', 'MERGE', 'UPSERT'
            ]

            query_upper = sql_query.upper()
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return False

        return True

    def _parse_and_format_query(self, sql_query: str) -> str:
        """
        Parse and format the SQL query
        """
        try:
            # Parse the query
            parsed = sqlparse.parse(sql_query)[0]

            # Format for better readability
            formatted = sqlparse.format(
                str(parsed),
                reindent=True,
                keyword_case='upper'
            )

            # Add LIMIT if not present
            if 'LIMIT' not in formatted.upper():
                formatted = f"{formatted.rstrip(';')} LIMIT {self.max_rows};"

            return formatted

        except Exception as e:
            logger.warning(f"Could not parse query, using original: {str(e)}")
            return sql_query

    def _execute_with_timeout(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute query with timeout protection
        """
        result = {'data': [], 'columns': [], 'row_count': 0}
        exception_container = [None]

        def query_executor():
            try:
                with connections['default'].cursor() as cursor:
                    cursor.execute(sql_query)

                    # Get column names
                    if cursor.description:
                        result['columns'] = [col[0] for col in cursor.description]

                        # Fetch results with row limit
                        rows = cursor.fetchmany(self.max_rows)
                        result['data'] = [[self._serialize_value(val) for val in row] for row in rows]
                        result['row_count'] = len(rows)

                        # Check if there are more rows
                        if cursor.fetchone():
                            result['truncated'] = True
                            logger.warning(f"Query results truncated to {self.max_rows} rows")
                    else:
                        # Query didn't return results (shouldn't happen with SELECT)
                        result['row_count'] = cursor.rowcount

            except Exception as e:
                exception_container[0] = e

        # Create and start thread
        thread = threading.Thread(target=query_executor)
        thread.daemon = True
        thread.start()

        # Wait for completion or timeout
        thread.join(timeout=self.timeout)

        if thread.is_alive():
            # Query is still running, it timed out
            raise QueryTimeoutException(f"Query execution timed out after {self.timeout} seconds")

        if exception_container[0]:
            raise exception_container[0]

        return result

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics including table row counts and relationships
        """
        try:
            with connections['default'].cursor() as cursor:
                # Get all tables first
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)

                tables = []
                total_rows = 0

                # Define table descriptions
                table_descriptions = {
                    'branches': 'Bank branch locations and contact information',
                    'customers': 'Customer personal and financial information',
                    'accounts': 'Bank accounts (checking, savings, etc.) with balances',
                    'transactions': 'All account transactions and transfers',
                    'credit_cards': 'Credit card information and limits',
                    'credit_card_transactions': 'Credit card purchases and payments',
                    'loans': 'Loan information (mortgages, personal, auto loans)',
                    'loan_payments': 'Individual loan payment records',
                    'auth_user': 'Django user accounts for system access',
                    'django_migrations': 'Database migration tracking',
                    'embeddings_schemaembedding': 'Schema embeddings for RAG system'
                }

                table_names = [row[0] for row in cursor.fetchall()]

                for table_name in table_names:
                    # Skip Django internal tables for cleaner display
                    if table_name.startswith(('auth_', 'django_')) or table_name == 'embeddings_schemaembedding':
                        continue

                    # Get accurate row count for each table
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]

                    tables.append({
                        'table_name': table_name,
                        'row_count': row_count,
                        'description': table_descriptions.get(table_name, f'Database table: {table_name}')
                    })
                    total_rows += row_count

                return {
                    'success': True,
                    'total_tables': len(tables),
                    'total_rows': total_rows,
                    'tables': tables,
                    'relationships': [
                        {'from': 'customers', 'to': 'accounts', 'type': 'one-to-many'},
                        {'from': 'customers', 'to': 'credit_cards', 'type': 'one-to-many'},
                        {'from': 'customers', 'to': 'loans', 'type': 'one-to-many'},
                        {'from': 'accounts', 'to': 'transactions', 'type': 'one-to-many'},
                        {'from': 'credit_cards', 'to': 'credit_card_transactions', 'type': 'one-to-many'},
                        {'from': 'loans', 'to': 'loan_payments', 'type': 'one-to-many'},
                        {'from': 'branches', 'to': 'customers', 'type': 'one-to-many'},
                        {'from': 'branches', 'to': 'accounts', 'type': 'one-to-many'}
                    ]
                }

        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection
        """
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()

            return {
                'success': True,
                'message': 'Database connection successful',
                'result': result[0] if result else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a specific table
        """
        try:
            query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """

            with connections['default'].cursor() as cursor:
                cursor.execute(query, [table_name])
                columns = cursor.fetchall()

            return {
                'success': True,
                'table_name': table_name,
                'columns': [
                    {
                        'name': col[0],
                        'type': col[1],
                        'nullable': col[2] == 'YES',
                        'default': col[3]
                    }
                    for col in columns
                ]
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_available_tables(self) -> List[str]:
        """
        Get list of available tables
        """
        try:
            query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """

            with connections['default'].cursor() as cursor:
                cursor.execute(query)
                tables = [row[0] for row in cursor.fetchall()]

            return tables
        except Exception as e:
            logger.error(f"Error getting available tables: {str(e)}")
            return []