import logging
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from django.conf import settings

from .models import SchemaEmbedding

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = "schema_embeddings"
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384,  # all-MiniLM-L6-v2 embedding size
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {str(e)}")

    def embed_schema(self, table_name: str, ddl_statement: str, description: str = "") -> str:
        """
        Create embeddings for a database schema and store in Qdrant
        """
        try:
            # Create text for embedding (DDL + description)
            text_to_embed = f"Table: {table_name}\n{ddl_statement}"
            if description:
                text_to_embed += f"\nDescription: {description}"

            # Generate embedding
            embedding = self.model.encode(text_to_embed).tolist()

            # Generate unique ID
            embedding_id = str(uuid.uuid4())

            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=embedding_id,
                        vector=embedding,
                        payload={
                            "table_name": table_name,
                            "ddl_statement": ddl_statement,
                            "description": description,
                            "text": text_to_embed
                        }
                    )
                ]
            )

            # Store in Django database
            schema_embedding, created = SchemaEmbedding.objects.update_or_create(
                table_name=table_name,
                defaults={
                    'ddl_statement': ddl_statement,
                    'description': description,
                    'embedding_id': embedding_id
                }
            )

            logger.info(f"Embedded schema for table: {table_name}")
            return embedding_id

        except Exception as e:
            logger.error(f"Error embedding schema for {table_name}: {str(e)}")
            raise

    def search_similar_schemas(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar schemas based on user query
        """
        try:
            # Generate embedding for the query
            query_embedding = self.model.encode(query).tolist()

            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True
            )

            # Format results
            results = []
            for result in search_results:
                results.append({
                    'table_name': result.payload['table_name'],
                    'ddl_statement': result.payload['ddl_statement'],
                    'description': result.payload.get('description', ''),
                    'score': result.score
                })

            logger.info(f"Found {len(results)} similar schemas for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Error searching similar schemas: {str(e)}")
            return []

    def embed_all_schemas(self, schema_definitions: List[Dict[str, str]]):
        """
        Embed multiple schema definitions at once
        """
        for schema in schema_definitions:
            try:
                self.embed_schema(
                    table_name=schema['table_name'],
                    ddl_statement=schema['ddl_statement'],
                    description=schema.get('description', '')
                )
            except Exception as e:
                logger.error(f"Failed to embed schema {schema['table_name']}: {str(e)}")

    def delete_schema_embedding(self, table_name: str):
        """
        Delete schema embedding from both Qdrant and Django database
        """
        try:
            # Get embedding from database
            schema_embedding = SchemaEmbedding.objects.get(table_name=table_name)

            # Delete from Qdrant
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[schema_embedding.embedding_id]
                )
            )

            # Delete from Django database
            schema_embedding.delete()

            logger.info(f"Deleted schema embedding for table: {table_name}")

        except SchemaEmbedding.DoesNotExist:
            logger.warning(f"Schema embedding not found for table: {table_name}")
        except Exception as e:
            logger.error(f"Error deleting schema embedding for {table_name}: {str(e)}")

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Get all stored schema information
        """
        schemas = SchemaEmbedding.objects.all()
        return [
            {
                'table_name': schema.table_name,
                'ddl_statement': schema.ddl_statement,
                'description': schema.description,
                'created_at': schema.created_at.isoformat()
            }
            for schema in schemas
        ]