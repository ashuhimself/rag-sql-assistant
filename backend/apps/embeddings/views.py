import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import EmbeddingService
from .serializers import SchemaEmbeddingSerializer, EmbedSchemaRequestSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
def embed_schema(request):
    """
    Create embeddings for a new schema
    """
    serializer = EmbedSchemaRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        embedding_service = EmbeddingService()
        embedding_id = embedding_service.embed_schema(
            table_name=serializer.validated_data['table_name'],
            ddl_statement=serializer.validated_data['ddl_statement'],
            description=serializer.validated_data.get('description', '')
        )

        return Response({
            'success': True,
            'embedding_id': embedding_id,
            'message': f"Schema for {serializer.validated_data['table_name']} embedded successfully"
        })

    except Exception as e:
        logger.error(f"Error embedding schema: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def search_schemas(request):
    """
    Search for similar schemas based on query
    """
    query = request.data.get('query', '')
    limit = request.data.get('limit', 3)

    if not query:
        return Response({
            'error': 'Query parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        embedding_service = EmbeddingService()
        results = embedding_service.search_similar_schemas(query, limit)

        return Response({
            'success': True,
            'results': results,
            'query': query
        })

    except Exception as e:
        logger.error(f"Error searching schemas: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_schemas(request):
    """
    List all embedded schemas
    """
    try:
        embedding_service = EmbeddingService()
        schemas = embedding_service.get_all_schemas()

        return Response({
            'success': True,
            'schemas': schemas,
            'count': len(schemas)
        })

    except Exception as e:
        logger.error(f"Error listing schemas: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_schema(request, table_name):
    """
    Delete a schema embedding
    """
    try:
        embedding_service = EmbeddingService()
        embedding_service.delete_schema_embedding(table_name)

        return Response({
            'success': True,
            'message': f"Schema for {table_name} deleted successfully"
        })

    except Exception as e:
        logger.error(f"Error deleting schema: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)