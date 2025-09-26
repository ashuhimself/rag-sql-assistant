import pytest
from django.test import TestCase
from unittest.mock import patch, Mock
from apps.embeddings.services import EmbeddingService
from apps.embeddings.models import SchemaEmbedding


class TestEmbeddingService(TestCase):
    def setUp(self):
        self.embedding_service = EmbeddingService()

    @patch('apps.embeddings.services.QdrantClient')
    @patch('apps.embeddings.services.SentenceTransformer')
    def test_embed_schema_success(self, mock_transformer, mock_qdrant):
        """Test successful schema embedding"""
        # Mock transformer
        mock_transformer_instance = Mock()
        mock_transformer_instance.encode.return_value = [0.1] * 384
        mock_transformer.return_value = mock_transformer_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant.return_value = mock_qdrant_instance

        table_name = 'customers'
        ddl_statement = 'CREATE TABLE customers (id INT, name VARCHAR(100));'
        description = 'Customer information'

        embedding_id = self.embedding_service.embed_schema(table_name, ddl_statement, description)

        # Check that embedding was stored in database
        schema_embedding = SchemaEmbedding.objects.get(table_name=table_name)
        self.assertEqual(schema_embedding.ddl_statement, ddl_statement)
        self.assertEqual(schema_embedding.description, description)
        self.assertEqual(schema_embedding.embedding_id, embedding_id)

        # Check that Qdrant upsert was called
        mock_qdrant_instance.upsert.assert_called_once()

    @patch('apps.embeddings.services.QdrantClient')
    @patch('apps.embeddings.services.SentenceTransformer')
    def test_search_similar_schemas(self, mock_transformer, mock_qdrant):
        """Test searching for similar schemas"""
        # Mock transformer
        mock_transformer_instance = Mock()
        mock_transformer_instance.encode.return_value = [0.1] * 384
        mock_transformer.return_value = mock_transformer_instance

        # Mock Qdrant client search results
        mock_result = Mock()
        mock_result.payload = {
            'table_name': 'customers',
            'ddl_statement': 'CREATE TABLE customers (id INT, name VARCHAR(100));',
            'description': 'Customer information'
        }
        mock_result.score = 0.9

        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [mock_result]
        mock_qdrant.return_value = mock_qdrant_instance

        query = "customer information"
        results = self.embedding_service.search_similar_schemas(query, limit=3)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['table_name'], 'customers')
        self.assertEqual(results[0]['score'], 0.9)

        # Check that search was called with correct parameters
        mock_qdrant_instance.search.assert_called_once()

    @patch('apps.embeddings.services.QdrantClient')
    @patch('apps.embeddings.services.SentenceTransformer')
    def test_delete_schema_embedding(self, mock_transformer, mock_qdrant):
        """Test deleting schema embedding"""
        # Create a schema embedding first
        schema_embedding = SchemaEmbedding.objects.create(
            table_name='test_table',
            ddl_statement='CREATE TABLE test_table (id INT);',
            embedding_id='test-uuid-123'
        )

        mock_qdrant_instance = Mock()
        mock_qdrant.return_value = mock_qdrant_instance

        self.embedding_service.delete_schema_embedding('test_table')

        # Check that embedding was deleted from database
        self.assertFalse(SchemaEmbedding.objects.filter(table_name='test_table').exists())

        # Check that Qdrant delete was called
        mock_qdrant_instance.delete.assert_called_once()

    def test_get_all_schemas(self):
        """Test retrieving all stored schemas"""
        # Create some test schemas
        SchemaEmbedding.objects.create(
            table_name='customers',
            ddl_statement='CREATE TABLE customers (id INT);',
            embedding_id='uuid-1'
        )
        SchemaEmbedding.objects.create(
            table_name='accounts',
            ddl_statement='CREATE TABLE accounts (id INT);',
            embedding_id='uuid-2'
        )

        schemas = self.embedding_service.get_all_schemas()

        self.assertEqual(len(schemas), 2)
        table_names = [schema['table_name'] for schema in schemas]
        self.assertIn('customers', table_names)
        self.assertIn('accounts', table_names)

    @patch('apps.embeddings.services.QdrantClient')
    @patch('apps.embeddings.services.SentenceTransformer')
    def test_embed_all_schemas(self, mock_transformer, mock_qdrant):
        """Test embedding multiple schemas at once"""
        mock_transformer_instance = Mock()
        mock_transformer_instance.encode.return_value = [0.1] * 384
        mock_transformer.return_value = mock_transformer_instance

        mock_qdrant_instance = Mock()
        mock_qdrant.return_value = mock_qdrant_instance

        schema_definitions = [
            {
                'table_name': 'customers',
                'ddl_statement': 'CREATE TABLE customers (id INT);',
                'description': 'Customer data'
            },
            {
                'table_name': 'accounts',
                'ddl_statement': 'CREATE TABLE accounts (id INT);',
                'description': 'Account data'
            }
        ]

        self.embedding_service.embed_all_schemas(schema_definitions)

        # Check that both schemas were created
        self.assertTrue(SchemaEmbedding.objects.filter(table_name='customers').exists())
        self.assertTrue(SchemaEmbedding.objects.filter(table_name='accounts').exists())

    @patch('apps.embeddings.services.QdrantClient')
    def test_ensure_collection_exists(self, mock_qdrant):
        """Test that collection is created if it doesn't exist"""
        mock_collections = Mock()
        mock_collections.collections = []

        mock_qdrant_instance = Mock()
        mock_qdrant_instance.get_collections.return_value = mock_collections
        mock_qdrant.return_value = mock_qdrant_instance

        # This will trigger collection creation
        service = EmbeddingService()

        # Check that create_collection was called
        mock_qdrant_instance.create_collection.assert_called_once()