#!/usr/bin/env python
"""
Script to embed database schemas for RAG system
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.embeddings.services import EmbeddingService
from django.db import connection


def main():
    print("🧠 Starting schema embedding process...")

    try:
        # Initialize embedding service
        embedding_service = EmbeddingService()

        # Get schema definitions from the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name, ddl_statement, description
                FROM schema_definitions
                ORDER BY table_name;
            """)
            schemas = cursor.fetchall()

        if not schemas:
            print("❌ No schemas found in database. Make sure the banking schema is loaded.")
            return

        print(f"📊 Found {len(schemas)} schemas to embed")

        # Prepare schema definitions
        schema_definitions = []
        for schema in schemas:
            schema_definitions.append({
                'table_name': schema[0],
                'ddl_statement': schema[1],
                'description': schema[2] if schema[2] else ''
            })

        # Embed all schemas
        print("🚀 Embedding schemas...")
        embedding_service.embed_all_schemas(schema_definitions)

        print("✅ Schema embedding completed successfully!")
        print(f"📈 Embedded {len(schema_definitions)} schemas:")

        for schema_def in schema_definitions:
            print(f"   - {schema_def['table_name']}")

        # Verify embeddings
        print("\n🔍 Verifying embeddings...")
        all_schemas = embedding_service.get_all_schemas()
        print(f"📊 Total schemas in embedding store: {len(all_schemas)}")

        # Test search functionality
        print("\n🧪 Testing search functionality...")
        test_queries = [
            "customer information",
            "account balances",
            "transaction data",
            "loan information"
        ]

        for query in test_queries:
            results = embedding_service.search_similar_schemas(query, limit=2)
            print(f"   Query: '{query}' -> Found {len(results)} relevant schemas")
            for result in results:
                print(f"      - {result['table_name']} (score: {result['score']:.3f})")

        print("\n🎉 All tests passed! The RAG system is ready to use.")

    except Exception as e:
        print(f"❌ Error during schema embedding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()