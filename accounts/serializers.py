import re
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import Profile
from todo_app.models import Task

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with strict email validation.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        email = value.strip().lower()
        if not email:
            raise serializers.ValidationError("Email address is required.")

        # Standard RFC email validation
        try:
            validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError("Please enter a valid email address.")

        # Additional domain structure validation
        if '@' not in email:
            raise serializers.ValidationError("Please enter a valid email address.")
        domain = email.split('@')[-1]
        if '.' not in domain or len(domain.split('.')[-1]) < 2:
            raise serializers.ValidationError("Email must have a valid domain extension (e.g. gmail.com).")

        # Uniqueness check
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("An account with this email address already exists.")

        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating users.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials. Please verify username and password.")
        if not user.is_active:
            raise serializers.ValidationError("This account has been disabled.")
        attrs['user'] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile info.
    """
    class Meta:
        model = Profile
        fields = ['bio', 'phone', 'location', 'updated_at']
        read_only_fields = ['updated_at']


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the currently logged in user, including profile & task metrics.
    """
    profile = ProfileSerializer(read_only=True)
    task_statistics = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'task_statistics']
        read_only_fields = ['id', 'username', 'task_statistics']

    def get_task_statistics(self, obj):
        tasks = Task.objects.filter(user=obj)
        total = tasks.count()
        completed = tasks.filter(completed=True).count()
        pending = total - completed
        rate = int((completed / total * 100)) if total > 0 else 0
        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'completion_rate_percentage': rate,
        }
