import pytest
from unittest.mock import Mock, patch
from utils.ollama_client import OllamaClient


class TestOllamaClient:
    def setup_method(self):
        self.ollama_client = OllamaClient()

    @patch('utils.ollama_client.requests.Session')
    def test_generate_sql_success(self, mock_session):
        """Test successful SQL generation"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': 'SELECT COUNT(*) FROM customers;'
        }
        mock_response.raise_for_status = Mock()

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        user_question = "How many customers do we have?"
        relevant_schemas = [
            {
                'table_name': 'customers',
                'ddl_statement': 'CREATE TABLE customers (id INT, name VARCHAR(100));',
                'description': 'Customer information'
            }
        ]

        result = self.ollama_client.generate_sql(user_question, relevant_schemas)

        self.assertEqual(result, 'SELECT COUNT(*) FROM customers;')
        mock_session_instance.post.assert_called_once()

    @patch('utils.ollama_client.requests.Session')
    def test_generate_sql_removes_markdown(self, mock_session):
        """Test that markdown formatting is removed from SQL"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': '```sql\nSELECT COUNT(*) FROM customers;\n```'
        }
        mock_response.raise_for_status = Mock()

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        user_question = "How many customers?"
        relevant_schemas = []

        result = self.ollama_client.generate_sql(user_question, relevant_schemas)

        self.assertEqual(result, 'SELECT COUNT(*) FROM customers;')

    @patch('utils.ollama_client.requests.Session')
    def test_generate_response_success(self, mock_session):
        """Test successful response generation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': 'The database contains 1,000 customers in total.'
        }
        mock_response.raise_for_status = Mock()

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        user_question = "How many customers do we have?"
        sql_query = "SELECT COUNT(*) FROM customers;"
        query_result = {
            'success': True,
            'data': [['1000']],
            'columns': ['count'],
            'row_count': 1
        }

        result = self.ollama_client.generate_response(user_question, sql_query, query_result)

        self.assertEqual(result, 'The database contains 1,000 customers in total.')

    @patch('utils.ollama_client.requests.Session')
    def test_generate_brief_response(self, mock_session):
        """Test brief response generation for non-database queries"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': "I'm a database assistant. Please ask about banking data."
        }
        mock_response.raise_for_status = Mock()

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        user_question = "What's the weather like?"
        result = self.ollama_client.generate_brief_response(user_question)

        self.assertEqual(result, "I'm a database assistant. Please ask about banking data.")

    @patch('utils.ollama_client.requests.Session')
    def test_test_connection_success(self, mock_session):
        """Test successful connection test"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': 'Hello'
        }
        mock_response.raise_for_status = Mock()

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        result = self.ollama_client.test_connection()

        self.assertTrue(result['success'])
        self.assertIn('Connected', result['message'])

    @patch('utils.ollama_client.requests.Session')
    def test_connection_error_handling(self, mock_session):
        """Test handling of connection errors"""
        mock_session_instance = Mock()
        mock_session_instance.post.side_effect = Exception("Connection failed")
        mock_session.return_value = mock_session_instance

        user_question = "test question"
        relevant_schemas = []

        with pytest.raises(Exception) as exc_info:
            self.ollama_client.generate_sql(user_question, relevant_schemas)

        self.assertIn("Failed to generate SQL", str(exc_info.value))

    @patch('utils.ollama_client.requests.Session')
    def test_generate_response_with_failed_query(self, mock_session):
        """Test response generation when query failed"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': 'I encountered an error with your query.'
        }
        mock_response.raise_for_status = Mock()

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        user_question = "Show me invalid data"
        sql_query = "SELECT * FROM nonexistent_table;"
        query_result = {
            'success': False,
            'error': 'Table does not exist'
        }

        result = self.ollama_client.generate_response(user_question, sql_query, query_result)

        self.assertEqual(result, 'I encountered an error with your query.')

    @patch('utils.ollama_client.requests.Session')
    def test_request_timeout_handling(self, mock_session):
        """Test handling of request timeouts"""
        mock_session_instance = Mock()
        mock_session_instance.post.side_effect = Exception("Request timeout")
        mock_session.return_value = mock_session_instance

        result = self.ollama_client.test_connection()

        self.assertFalse(result['success'])
        self.assertIn('Request timeout', result['error'])

    def test_make_request_payload_structure(self):
        """Test that request payload has correct structure"""
        with patch.object(self.ollama_client.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {'response': 'test'}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            self.ollama_client._make_request("test prompt", "test system")

            call_args = mock_post.call_args
            payload = call_args[1]['json']

            self.assertIn('model', payload)
            self.assertIn('prompt', payload)
            self.assertIn('system', payload)
            self.assertIn('stream', payload)
            self.assertIn('options', payload)
            self.assertFalse(payload['stream'])