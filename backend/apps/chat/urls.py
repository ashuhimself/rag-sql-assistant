from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('sessions/', views.list_sessions, name='list_sessions'),
    path('sessions/<str:session_id>/', views.get_session, name='get_session'),
]