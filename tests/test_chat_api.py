import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.chat.models import ChatSession, ChatMessage


class TestChatAPI(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_chat_endpoint_creates_session(self):
        """Test that chat endpoint creates a new session"""
        data = {
            'message': 'How many customers do we have?'
        }

        with pytest.mock.patch('apps.chat.views._handle_database_query') as mock_handler:
            mock_handler.return_value = ("We have 1000 customers.", "SELECT COUNT(*) FROM customers;", {'count': 1000})

            response = self.client.post('/api/chat/', data, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertIn('session_id', response.data)

            # Check that session was created
            session_id = response.data['session_id']
            self.assertTrue(ChatSession.objects.filter(session_id=session_id).exists())

    def test_chat_endpoint_with_existing_session(self):
        """Test chat with existing session"""
        session = ChatSession.objects.create(session_id='test-session-123')

        data = {
            'message': 'Show me account balances',
            'session_id': session.session_id
        }

        with pytest.mock.patch('apps.chat.views._handle_database_query') as mock_handler:
            mock_handler.return_value = ("Here are the account balances.", "SELECT * FROM accounts;", [])

            response = self.client.post('/api/chat/', data, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['session_id'], session.session_id)

    def test_get_session_endpoint(self):
        """Test retrieving a session with messages"""
        session = ChatSession.objects.create(session_id='test-session-456')
        ChatMessage.objects.create(
            session=session,
            message_type='user',
            content='Test message'
        )

        response = self.client.get(f'/api/chat/sessions/{session.session_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['session_id'], session.session_id)
        self.assertEqual(len(response.data['messages']), 1)

    def test_list_sessions_endpoint(self):
        """Test listing all sessions"""
        ChatSession.objects.create(session_id='session-1')
        ChatSession.objects.create(session_id='session-2')

        response = self.client.get('/api/chat/sessions/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_invalid_message_format(self):
        """Test validation of message format"""
        data = {
            'message': ''  # Empty message
        }

        response = self.client.post('/api/chat/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_database_query_detection(self):
        """Test detection of database-related queries"""
        from apps.chat.views import _is_database_query

        # Should detect database queries
        self.assertTrue(_is_database_query("How many customers do we have?"))
        self.assertTrue(_is_database_query("Show me all accounts"))
        self.assertTrue(_is_database_query("List transactions from yesterday"))

        # Should not detect general queries
        self.assertFalse(_is_database_query("What's the weather like?"))
        self.assertFalse(_is_database_query("Tell me a joke"))


@pytest.mark.django_db
class TestChatIntegration:
    def test_full_chat_flow(self, mock_ollama_client, mock_qdrant_client, mock_sentence_transformer):
        """Test complete chat flow with mocked AI services"""
        client = APIClient()

        # Mock the embedding service
        with pytest.mock.patch('apps.embeddings.services.EmbeddingService') as mock_embedding:
            mock_embedding_instance = mock_embedding.return_value
            mock_embedding_instance.search_similar_schemas.return_value = [
                {
                    'table_name': 'customers',
                    'ddl_statement': 'CREATE TABLE customers (id INT, name VARCHAR(100));',
                    'description': 'Customer information',
                    'score': 0.9
                }
            ]

            # Mock the database service
            with pytest.mock.patch('apps.database.services.DatabaseService') as mock_db:
                mock_db_instance = mock_db.return_value
                mock_db_instance.execute_safe_query.return_value = {
                    'success': True,
                    'data': [['1000']],
                    'columns': ['count'],
                    'row_count': 1
                }

                data = {
                    'message': 'How many customers do we have?'
                }

                response = client.post('/api/chat/', data, format='json')

                assert response.status_code == status.HTTP_200_OK
                assert response.data['success'] is True
                assert 'session_id' in response.data
                assert response.data['message']['message_type'] == 'assistant'