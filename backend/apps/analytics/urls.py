from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_data, name='analyze_data'),
    path('metrics/', views.business_metrics, name='business_metrics'),
    path('cohort/', views.cohort_analysis, name='cohort_analysis'),
    path('reports/', views.analysis_reports, name='analysis_reports'),
    path('reports/<int:report_id>/', views.analysis_report_detail, name='analysis_report_detail'),
    path('insights/', views.smart_insights, name='smart_insights'),
]