from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', include('apps.chat.urls')),
    path('api/embeddings/', include('apps.embeddings.urls')),
    path('api/database/', include('apps.database.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]