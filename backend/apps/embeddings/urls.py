from django.urls import path
from . import views

urlpatterns = [
    path('embed/', views.embed_schema, name='embed_schema'),
    path('search/', views.search_schemas, name='search_schemas'),
    path('schemas/', views.list_schemas, name='list_schemas'),
    path('schemas/<str:table_name>/', views.delete_schema, name='delete_schema'),
]