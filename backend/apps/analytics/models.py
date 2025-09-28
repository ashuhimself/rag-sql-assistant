from django.db import models
from apps.chat.models import ChatSession


class AnalysisReport(models.Model):
    """Store comprehensive analysis reports"""
    ANALYSIS_TYPES = [
        ('descriptive', 'Descriptive Statistics'),
        ('diagnostic', 'Diagnostic Analysis'),
        ('predictive', 'Predictive Analysis'),
        ('prescriptive', 'Prescriptive Analysis'),
        ('cohort', 'Cohort Analysis'),
        ('trend', 'Trend Analysis'),
        ('correlation', 'Correlation Analysis'),
        ('outlier', 'Outlier Detection'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='analysis_reports')
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    query_executed = models.TextField()
    raw_data = models.JSONField(default=dict)
    statistical_insights = models.JSONField(default=dict)
    visualizations = models.JSONField(default=list)
    recommendations = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class DataInsight(models.Model):
    """Store individual data insights and patterns"""
    INSIGHT_TYPES = [
        ('trend', 'Trend'),
        ('anomaly', 'Anomaly'),
        ('correlation', 'Correlation'),
        ('pattern', 'Pattern'),
        ('threshold', 'Threshold Alert'),
        ('forecast', 'Forecast'),
    ]

    report = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE, related_name='insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    significance_level = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-significance_level', '-created_at']


class BusinessMetric(models.Model):
    """Track key business metrics over time"""
    METRIC_CATEGORIES = [
        ('customer', 'Customer Metrics'),
        ('financial', 'Financial Metrics'),
        ('operational', 'Operational Metrics'),
        ('risk', 'Risk Metrics'),
        ('growth', 'Growth Metrics'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=METRIC_CATEGORIES)
    value = models.FloatField()
    unit = models.CharField(max_length=50, default='count')
    calculation_method = models.TextField()
    sql_query = models.TextField()
    benchmark_value = models.FloatField(null=True, blank=True)
    target_value = models.FloatField(null=True, blank=True)
    is_kpi = models.BooleanField(default=False)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-calculated_at']
        unique_together = ['name', 'calculated_at']