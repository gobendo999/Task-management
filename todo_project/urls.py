from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI Schema & Interactive Swagger UI Endpoints
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='api-docs'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # RESTful API Endpoints
    path('api/', include('todo_project.api_urls')),

    # Frontend Web Views
    path('', include('accounts.urls')),
    path('', include('todo_app.urls')),
]