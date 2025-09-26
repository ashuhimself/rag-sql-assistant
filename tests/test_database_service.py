import pytest
from django.test import TestCase
from unittest.mock import patch, Mock
from apps.database.services import DatabaseService, QueryTimeoutException


class TestDatabaseService(TestCase):
    def setUp(self):
        self.db_service = DatabaseService()

    def test_safe_query_validation_allows_select(self):
        """Test that SELECT queries are allowed"""
        safe_queries = [
            "SELECT * FROM customers;",
            "SELECT name, email FROM customers WHERE id = 1;",
            "SELECT COUNT(*) FROM accounts;",
            "WITH cte AS (SELECT * FROM customers) SELECT * FROM cte;",
        ]

        for query in safe_queries:
            result = self.db_service._is_safe_query(query)
            self.assertTrue(result, f"Query should be safe: {query}")

    def test_safe_query_validation_blocks_dangerous(self):
        """Test that dangerous queries are blocked"""
        dangerous_queries = [
            "INSERT INTO customers VALUES (1, 'test');",
            "UPDATE customers SET name = 'test';",
            "DELETE FROM customers;",
            "DROP TABLE customers;",
            "CREATE TABLE test (id INT);",
            "ALTER TABLE customers ADD COLUMN test VARCHAR(50);",
            "TRUNCATE TABLE customers;",
        ]

        for query in dangerous_queries:
            result = self.db_service._is_safe_query(query)
            self.assertFalse(result, f"Query should be blocked: {query}")

    def test_query_formatting_adds_limit(self):
        """Test that LIMIT is added to queries without it"""
        query = "SELECT * FROM customers"
        formatted = self.db_service._parse_and_format_query(query)

        self.assertIn('LIMIT', formatted.upper())
        self.assertIn(str(self.db_service.max_rows), formatted)

    def test_query_formatting_preserves_existing_limit(self):
        """Test that existing LIMIT is preserved"""
        query = "SELECT * FROM customers LIMIT 5"
        formatted = self.db_service._parse_and_format_query(query)

        # Should not add another LIMIT
        limit_count = formatted.upper().count('LIMIT')
        self.assertEqual(limit_count, 1)

    @patch('apps.database.services.connections')
    def test_execute_safe_query_success(self, mock_connections):
        """Test successful query execution"""
        # Mock cursor
        mock_cursor = Mock()
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchmany.return_value = [(1, 'John'), (2, 'Jane')]
        mock_cursor.fetchone.return_value = None

        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connections.__getitem__.return_value = mock_connection

        result = self.db_service.execute_safe_query("SELECT * FROM customers LIMIT 10")

        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 2)
        self.assertEqual(result['columns'], ['id', 'name'])
        self.assertEqual(result['row_count'], 2)

    @patch('apps.database.services.connections')
    def test_execute_safe_query_with_unsafe_query(self, mock_connections):
        """Test that unsafe queries are rejected"""
        result = self.db_service.execute_safe_query("DROP TABLE customers;")

        self.assertFalse(result['success'])
        self.assertIn('unsafe', result['error'].lower())

    @patch('apps.database.services.connections')
    def test_test_connection_success(self, mock_connections):
        """Test successful database connection test"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)

        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connections.__getitem__.return_value = mock_connection

        result = self.db_service.test_connection()

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 1)

    @patch('apps.database.services.connections')
    def test_get_table_info_success(self, mock_connections):
        """Test retrieving table information"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ('id', 'integer', 'NO', None),
            ('name', 'character varying', 'YES', 'Anonymous')
        ]

        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connections.__getitem__.return_value = mock_connection

        result = self.db_service.get_table_info('customers')

        self.assertTrue(result['success'])
        self.assertEqual(result['table_name'], 'customers')
        self.assertEqual(len(result['columns']), 2)
        self.assertEqual(result['columns'][0]['name'], 'id')
        self.assertFalse(result['columns'][0]['nullable'])

    @patch('apps.database.services.connections')
    def test_get_available_tables_success(self, mock_connections):
        """Test retrieving list of available tables"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ('customers',),
            ('accounts',),
            ('transactions',)
        ]

        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connections.__getitem__.return_value = mock_connection

        tables = self.db_service.get_available_tables()

        self.assertEqual(len(tables), 3)
        self.assertIn('customers', tables)
        self.assertIn('accounts', tables)
        self.assertIn('transactions', tables)

    def test_query_timeout_handling(self):
        """Test that query timeout is handled properly"""
        # This is a more complex test that would require threading
        # For now, we'll test the timeout configuration
        self.assertIsInstance(self.db_service.timeout, int)
        self.assertGreater(self.db_service.timeout, 0)

    def test_row_limit_configuration(self):
        """Test that row limit is properly configured"""
        self.assertIsInstance(self.db_service.max_rows, int)
        self.assertGreater(self.db_service.max_rows, 0)