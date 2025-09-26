import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import DatabaseService
from .serializers import QueryRequestSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
def execute_query(request):
    """
    Execute a SQL query safely
    """
    serializer = QueryRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    sql_query = serializer.validated_data['query']

    try:
        db_service = DatabaseService()
        result = db_service.execute_safe_query(sql_query)

        return Response(result)

    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def test_connection(request):
    """
    Test database connection
    """
    try:
        db_service = DatabaseService()
        result = db_service.test_connection()
        return Response(result)

    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_tables(request):
    """
    Get list of available tables
    """
    try:
        db_service = DatabaseService()
        tables = db_service.get_available_tables()

        return Response({
            'success': True,
            'tables': tables,
            'count': len(tables)
        })

    except Exception as e:
        logger.error(f"Error listing tables: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def table_info(request, table_name):
    """
    Get information about a specific table
    """
    try:
        db_service = DatabaseService()
        result = db_service.get_table_info(table_name)
        return Response(result)

    except Exception as e:
        logger.error(f"Error getting table info: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def database_stats(request):
    """
    Get database statistics including table row counts
    """
    try:
        db_service = DatabaseService()
        stats = db_service.get_database_stats()
        return Response(stats)

    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)