from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from todo_app.api_views import TaskViewSet
from accounts.api_views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
)

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    # Task API endpoints (/api/tasks/)
    path('', include(router.urls)),

    # Accounts API endpoints (/api/auth/...)
    path('auth/register/', RegisterAPIView.as_view(), name='api_register'),
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('auth/user/', CurrentUserAPIView.as_view(), name='api_current_user'),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
]
