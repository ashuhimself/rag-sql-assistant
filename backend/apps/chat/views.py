import uuid
import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

from .models import ChatSession, ChatMessage
from .serializers import ChatRequestSerializer, ChatSessionSerializer, ChatMessageSerializer
from apps.embeddings.services import EmbeddingService
from apps.database.services import DatabaseService
from utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


@api_view(['POST'])
def chat(request):
    """
    Handle chat messages and generate SQL queries using RAG
    """
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    message = serializer.validated_data['message']
    session_id = serializer.validated_data.get('session_id', str(uuid.uuid4()))

    try:
        # Get or create chat session
        session, created = ChatSession.objects.get_or_create(session_id=session_id)

        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )

        # Check if this is a database-related query
        if _is_database_query(message):
            response_content, sql_query, sql_result = _handle_database_query(message)
        else:
            response_content = _handle_general_query(message)
            sql_query = None
            sql_result = None

        # Save assistant response
        assistant_message = ChatMessage.objects.create(
            session=session,
            message_type='assistant',
            content=response_content,
            sql_query=sql_query,
            sql_result=sql_result
        )

        return Response({
            'session_id': session_id,
            'message': ChatMessageSerializer(assistant_message).data,
            'success': True
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return Response({
            'error': 'An error occurred processing your request',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_session(request, session_id):
    """
    Retrieve a chat session with all messages
    """
    try:
        session = ChatSession.objects.get(session_id=session_id)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_sessions(request):
    """
    List all chat sessions
    """
    sessions = ChatSession.objects.all()[:20]  # Limit to recent 20 sessions
    serializer = ChatSessionSerializer(sessions, many=True)
    return Response(serializer.data)


def _is_database_query(message: str) -> bool:
    """
    Determine if the message is asking for database information
    """
    database_keywords = [
        'show', 'select', 'query', 'database', 'table', 'customer', 'account',
        'transaction', 'loan', 'payment', 'branch', 'how many', 'count',
        'list', 'find', 'search', 'get', 'retrieve', 'display'
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in database_keywords)


def _handle_database_query(message: str) -> tuple:
    """
    Handle database-related queries using RAG
    """
    try:
        # Get relevant schema using embeddings
        embedding_service = EmbeddingService()
        relevant_schemas = embedding_service.search_similar_schemas(message)

        # Generate SQL query using Ollama
        ollama_client = OllamaClient()
        sql_query = ollama_client.generate_sql(message, relevant_schemas)

        # Execute SQL query
        db_service = DatabaseService()
        result = db_service.execute_safe_query(sql_query)

        # Generate natural language response
        response = ollama_client.generate_response(message, sql_query, result)

        return response, sql_query, result

    except Exception as e:
        logger.error(f"Error handling database query: {str(e)}")
        return f"Sorry, I encountered an error while processing your query: {str(e)}", None, None


def _handle_general_query(message: str) -> str:
    """
    Handle non-database queries with brief responses
    """
    try:
        ollama_client = OllamaClient()
        response = ollama_client.generate_brief_response(message)
        return response
    except Exception as e:
        logger.error(f"Error handling general query: {str(e)}")
        return "I'm designed to help with database queries. Please ask about customers, accounts, transactions, loans, or other banking data."