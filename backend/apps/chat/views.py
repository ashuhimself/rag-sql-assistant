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
from utils.llm_client import LLMClient

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
    Handle database-related queries using RAG and analytics
    """
    try:
        # Get relevant schema using embeddings
        embedding_service = EmbeddingService()
        relevant_schemas = embedding_service.search_similar_schemas(message)

        # Generate SQL query using LLM
        llm_client = LLMClient()
        sql_query = llm_client.generate_sql(message, relevant_schemas)

        # Execute SQL query
        db_service = DatabaseService()
        result = db_service.execute_safe_query(sql_query)

        # Perform analytics if query was successful and returned data
        analysis_result = None
        if result.get('success') and result.get('data'):
            try:
                from apps.analytics.services import AnalyticsService
                analytics_service = AnalyticsService()

                # Determine analysis type based on query content
                analysis_type = _determine_analysis_type(message)
                analysis_result = analytics_service.analyze_query_result(sql_query, result, analysis_type)

                # Enhance response with insights
                if analysis_result and not analysis_result.get('error'):
                    enhanced_response = _generate_enhanced_response(message, sql_query, result, analysis_result, llm_client)
                    return enhanced_response, sql_query, {**result, 'analysis': analysis_result}

            except Exception as analytics_error:
                logger.warning(f"Analytics failed, using basic response: {str(analytics_error)}")

        # Generate standard natural language response
        response = llm_client.generate_response(message, sql_query, result)

        # Add analysis result if available
        final_result = result
        if analysis_result and not analysis_result.get('error'):
            final_result = {**result, 'analysis': analysis_result}

        return response, sql_query, final_result

    except Exception as e:
        logger.error(f"Error handling database query: {str(e)}")
        return f"Sorry, I encountered an error while processing your query: {str(e)}", None, None


def _determine_analysis_type(message: str) -> str:
    """Determine the appropriate analysis type based on the user's message"""
    message_lower = message.lower()

    if any(word in message_lower for word in ['trend', 'over time', 'timeline', 'monthly', 'yearly']):
        return 'trend'
    elif any(word in message_lower for word in ['outlier', 'anomaly', 'unusual', 'strange']):
        return 'outlier'
    elif any(word in message_lower for word in ['correlation', 'relationship', 'connect', 'relate']):
        return 'correlation'
    elif any(word in message_lower for word in ['cohort', 'retention', 'segment']):
        return 'cohort'
    elif any(word in message_lower for word in ['predict', 'forecast', 'future']):
        return 'predictive'
    else:
        return 'descriptive'


def _generate_enhanced_response(message: str, sql_query: str, result: dict, analysis: dict, llm_client) -> str:
    """Generate enhanced response with analytics insights"""
    try:
        # Start with basic response
        base_response = llm_client.generate_response(message, sql_query, result)

        # Add key insights
        insights = analysis.get('insights', [])
        if insights:
            insight_text = "\n\n📊 **Key Insights:**\n"
            for i, insight in enumerate(insights[:3]):  # Top 3 insights
                insight_text += f"{i+1}. {insight.get('title', '')}\n"
            base_response += insight_text

        # Add recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            rec_text = "\n\n💡 **Recommendations:**\n"
            for i, rec in enumerate(recommendations[:2]):  # Top 2 recommendations
                rec_text += f"• {rec}\n"
            base_response += rec_text

        # Add statistical summary for numeric data
        descriptive = analysis.get('descriptive', {})
        numeric_summary = descriptive.get('numeric_summary', {})
        if numeric_summary:
            stats_text = "\n\n📈 **Statistical Summary:**\n"
            describe_data = numeric_summary.get('describe', {})
            for col, stats in list(describe_data.items())[:2]:  # Limit to 2 columns
                if isinstance(stats, dict) and 'mean' in stats:
                    stats_text += f"• {col}: Mean {stats['mean']:.2f}, Std {stats.get('std', 0):.2f}\n"
            base_response += stats_text

        return base_response

    except Exception as e:
        logger.warning(f"Could not enhance response: {str(e)}")
        return llm_client.generate_response(message, sql_query, result)


def _handle_general_query(message: str) -> str:
    """
    Handle non-database queries with brief responses
    """
    try:
        llm_client = LLMClient()
        response = llm_client.generate_brief_response(message)
        return response
    except Exception as e:
        logger.error(f"Error handling general query: {str(e)}")
        return "I'm designed to help with database queries. Please ask about customers, accounts, transactions, loans, or other banking data."