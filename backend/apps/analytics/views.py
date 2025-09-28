import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .services import AnalyticsService
from .serializers import (
    AnalyticsRequestSerializer,
    CohortAnalysisRequestSerializer,
    BusinessMetricsRequestSerializer,
    AnalysisReportSerializer
)
from .models import AnalysisReport, DataInsight
from apps.database.services import DatabaseService
from apps.chat.models import ChatSession

logger = logging.getLogger(__name__)


@api_view(['POST'])
def analyze_data(request):
    """
    Perform comprehensive data analysis on a SQL query result
    """
    serializer = AnalyticsRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data['query']
    analysis_type = serializer.validated_data['analysis_type']
    session_id = serializer.validated_data.get('session_id')

    try:
        # Execute the query first
        db_service = DatabaseService()
        query_result = db_service.execute_safe_query(query)

        if not query_result.get('success'):
            return Response({
                'error': 'Query execution failed',
                'query_error': query_result.get('error'),
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)

        # Perform analytics
        analytics_service = AnalyticsService()
        analysis = analytics_service.analyze_query_result(query, query_result, analysis_type)

        if 'error' in analysis:
            return Response({
                'error': analysis['error'],
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save analysis report if session_id provided
        if session_id:
            try:
                session, _ = ChatSession.objects.get_or_create(session_id=session_id)

                # Create analysis report
                report = AnalysisReport.objects.create(
                    session=session,
                    analysis_type=analysis_type,
                    query_executed=query,
                    raw_data=query_result,
                    statistical_insights=analysis.get('statistical', {}),
                    visualizations=analysis.get('visualizations', []),
                    recommendations='\n'.join(analysis.get('recommendations', [])),
                    confidence_score=0.8  # Default confidence
                )

                # Create data insights
                for insight in analysis.get('insights', []):
                    DataInsight.objects.create(
                        report=report,
                        insight_type=insight.get('type', 'pattern'),
                        title=insight.get('title', ''),
                        description=insight.get('description', ''),
                        metric_name=insight.get('metric', ''),
                        metric_value=insight.get('value', 0),
                        significance_level=insight.get('significance', 0)
                    )

                analysis['report_id'] = report.id

            except Exception as e:
                logger.warning(f"Could not save analysis report: {str(e)}")

        return Response({
            'success': True,
            'query_result': query_result,
            'analysis': analysis,
            'analysis_type': analysis_type
        })

    except Exception as e:
        logger.error(f"Error in data analysis: {str(e)}")
        return Response({
            'error': f'Analysis failed: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def business_metrics(request):
    """
    Calculate and return key business metrics
    """
    try:
        # Check cache first
        cache_key = 'business_metrics_dashboard'
        cached_metrics = cache.get(cache_key)

        if cached_metrics:
            return Response({
                'success': True,
                'metrics': cached_metrics,
                'cached': True
            })

        # Calculate metrics
        analytics_service = AnalyticsService()
        metrics_result = analytics_service.calculate_business_metrics()

        if metrics_result.get('success'):
            # Cache for 15 minutes
            cache.set(cache_key, metrics_result['metrics'], 900)

            return Response({
                'success': True,
                'metrics': metrics_result['metrics'],
                'calculated_at': metrics_result['calculated_at'],
                'cached': False
            })
        else:
            return Response({
                'error': metrics_result.get('error', 'Failed to calculate metrics'),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error calculating business metrics: {str(e)}")
        return Response({
            'error': f'Metrics calculation failed: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def cohort_analysis(request):
    """
    Perform cohort analysis
    """
    serializer = CohortAnalysisRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    cohort_type = serializer.validated_data['cohort_type']
    time_period = serializer.validated_data['time_period']

    try:
        analytics_service = AnalyticsService()
        cohort_result = analytics_service.perform_cohort_analysis(cohort_type)

        if cohort_result.get('success'):
            return Response({
                'success': True,
                'cohort_analysis': cohort_result,
                'time_period': time_period
            })
        else:
            return Response({
                'error': cohort_result.get('error', 'Cohort analysis failed'),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error in cohort analysis: {str(e)}")
        return Response({
            'error': f'Cohort analysis failed: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def analysis_reports(request):
    """
    Get saved analysis reports
    """
    try:
        session_id = request.GET.get('session_id')

        if session_id:
            reports = AnalysisReport.objects.filter(session__session_id=session_id)
        else:
            reports = AnalysisReport.objects.all()[:20]  # Latest 20 reports

        serializer = AnalysisReportSerializer(reports, many=True)

        return Response({
            'success': True,
            'reports': serializer.data
        })

    except Exception as e:
        logger.error(f"Error fetching analysis reports: {str(e)}")
        return Response({
            'error': f'Failed to fetch reports: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def analysis_report_detail(request, report_id):
    """
    Get detailed analysis report
    """
    try:
        report = AnalysisReport.objects.get(id=report_id)
        serializer = AnalysisReportSerializer(report)

        return Response({
            'success': True,
            'report': serializer.data
        })

    except AnalysisReport.DoesNotExist:
        return Response({
            'error': 'Analysis report not found',
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error fetching analysis report: {str(e)}")
        return Response({
            'error': f'Failed to fetch report: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def smart_insights(request):
    """
    Generate smart insights based on natural language query
    """
    try:
        user_query = request.data.get('query', '').lower()

        # Determine appropriate analysis based on query keywords
        if any(word in user_query for word in ['trend', 'over time', 'timeline', 'monthly', 'yearly']):
            analysis_type = 'trend'
        elif any(word in user_query for word in ['outlier', 'anomaly', 'unusual', 'strange']):
            analysis_type = 'outlier'
        elif any(word in user_query for word in ['correlation', 'relationship', 'connect', 'relate']):
            analysis_type = 'correlation'
        elif any(word in user_query for word in ['cohort', 'retention', 'segment']):
            analysis_type = 'cohort'
        else:
            analysis_type = 'descriptive'

        # Generate appropriate SQL query based on user intent
        analytics_service = AnalyticsService()
        db_service = DatabaseService()

        # Smart query generation based on keywords
        if 'customer' in user_query:
            if 'high value' in user_query or 'premium' in user_query:
                sql_query = """
                    SELECT customer_segment, COUNT(*) as count, AVG(annual_income) as avg_income,
                           AVG(credit_score) as avg_credit_score
                    FROM customers
                    WHERE customer_segment = 'premium' OR annual_income > 100000
                    GROUP BY customer_segment
                """
            else:
                sql_query = """
                    SELECT customer_segment, risk_category, COUNT(*) as count,
                           AVG(credit_score) as avg_credit_score, AVG(annual_income) as avg_income
                    FROM customers
                    GROUP BY customer_segment, risk_category
                    ORDER BY count DESC
                """
        elif 'transaction' in user_query:
            sql_query = """
                SELECT transaction_type, merchant_category,
                       COUNT(*) as transaction_count, SUM(amount) as total_amount,
                       AVG(amount) as avg_amount
                FROM transactions
                WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY transaction_type, merchant_category
                ORDER BY total_amount DESC
            """
        elif 'loan' in user_query:
            sql_query = """
                SELECT loan_type, loan_status, COUNT(*) as loan_count,
                       SUM(loan_amount) as total_amount, AVG(interest_rate) as avg_rate
                FROM loans
                GROUP BY loan_type, loan_status
                ORDER BY total_amount DESC
            """
        else:
            # Default dashboard query
            sql_query = """
                SELECT 'customers' as metric, COUNT(*) as value FROM customers
                UNION ALL
                SELECT 'accounts' as metric, COUNT(*) as value FROM accounts
                UNION ALL
                SELECT 'loans' as metric, COUNT(*) as value FROM loans
                UNION ALL
                SELECT 'transactions_30d' as metric, COUNT(*) as value
                FROM transactions WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
            """

        # Execute query and analyze
        query_result = db_service.execute_safe_query(sql_query)

        if query_result.get('success'):
            analysis = analytics_service.analyze_query_result(sql_query, query_result, analysis_type)

            return Response({
                'success': True,
                'query': user_query,
                'generated_sql': sql_query,
                'analysis_type': analysis_type,
                'query_result': query_result,
                'insights': analysis
            })
        else:
            return Response({
                'error': 'Query execution failed',
                'query_error': query_result.get('error'),
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error generating smart insights: {str(e)}")
        return Response({
            'error': f'Smart insights generation failed: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)