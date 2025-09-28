from rest_framework import serializers
from .models import AnalysisReport, DataInsight, BusinessMetric


class DataInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataInsight
        fields = '__all__'


class AnalysisReportSerializer(serializers.ModelSerializer):
    insights = DataInsightSerializer(many=True, read_only=True)

    class Meta:
        model = AnalysisReport
        fields = '__all__'


class BusinessMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMetric
        fields = '__all__'


class AnalyticsRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=5000)
    analysis_type = serializers.ChoiceField(
        choices=[
            ('descriptive', 'Descriptive Statistics'),
            ('diagnostic', 'Diagnostic Analysis'),
            ('predictive', 'Predictive Analysis'),
            ('prescriptive', 'Prescriptive Analysis'),
            ('cohort', 'Cohort Analysis'),
            ('trend', 'Trend Analysis'),
            ('correlation', 'Correlation Analysis'),
            ('outlier', 'Outlier Detection'),
        ],
        default='descriptive'
    )
    session_id = serializers.CharField(max_length=100, required=False)


class CohortAnalysisRequestSerializer(serializers.Serializer):
    cohort_type = serializers.ChoiceField(
        choices=[
            ('customer_acquisition', 'Customer Acquisition Cohort'),
            ('transaction_behavior', 'Transaction Behavior Cohort'),
            ('loan_performance', 'Loan Performance Cohort'),
        ],
        default='customer_acquisition'
    )
    time_period = serializers.ChoiceField(
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly'),
        ],
        default='monthly'
    )


class BusinessMetricsRequestSerializer(serializers.Serializer):
    metrics = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('customer', 'Customer Metrics'),
            ('financial', 'Financial Metrics'),
            ('operational', 'Operational Metrics'),
            ('risk', 'Risk Metrics'),
            ('growth', 'Growth Metrics'),
        ]),
        required=False,
        default=['customer', 'financial', 'operational']
    )
    time_range = serializers.ChoiceField(
        choices=[
            ('1d', 'Last 24 Hours'),
            ('7d', 'Last 7 Days'),
            ('30d', 'Last 30 Days'),
            ('90d', 'Last 90 Days'),
            ('1y', 'Last Year'),
        ],
        default='30d'
    )