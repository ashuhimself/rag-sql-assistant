from django.urls import path
from . import views

urlpatterns = [
    path('execute/', views.execute_query, name='execute_query'),
    path('test/', views.test_connection, name='test_connection'),
    path('stats/', views.database_stats, name='database_stats'),
    path('tables/', views.list_tables, name='list_tables'),
    path('tables/<str:table_name>/', views.table_info, name='table_info'),
]