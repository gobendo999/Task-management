from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, LoginSerializer, CurrentUserSerializer


class RegisterAPIView(APIView):
    """
    Endpoint for creating new user accounts.
    Requires a valid and unique email address. Generates and returns auth token.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="User Registration",
        description="Register a new user account with a valid, unique email address and secure password. Returns auth token for mobile and external clients.",
        request=RegisterSerializer,
        responses={201: CurrentUserSerializer}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': f"Account successfully created for {user.username}!",
                'token': token.key,
                'user': CurrentUserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """
    Endpoint to authenticate user credentials, start a session, and return auth token.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        summary="User Login",
        description="Authenticate user with username and password. Returns session and token for cross-platform authentication.",
        request=LoginSerializer,
        responses={200: CurrentUserSerializer}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': f"Welcome back, {user.username}! Session and token authenticated.",
                'token': token.key,
                'user': CurrentUserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    Endpoint to end current user session and revoke token.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User Logout",
        description="End active user session and revoke auth token.",
        request=None,
        responses={200: dict}
    )
    def post(self, request):
        username = request.user.username
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({'message': f"Successfully logged out {username} and revoked token."}, status=status.HTTP_200_OK)


class CurrentUserAPIView(APIView):
    """
    Endpoint to retrieve authenticated user profile and live task metrics.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Current User & Task Stats",
        description="Retrieve profile details and live task statistics for the currently logged-in user.",
        responses={200: CurrentUserSerializer}
    )
    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
