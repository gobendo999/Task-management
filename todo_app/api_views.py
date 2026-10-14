from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import Task
from .serializers import TaskSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List User Tasks",
        description="Retrieve all tasks belonging to the authenticated user. Supports search and status filtering.",
        parameters=[
            OpenApiParameter(name='q', description='Search title or description', required=False, type=str),
            OpenApiParameter(name='status', description='Filter by status: all, completed, or pending', required=False, type=str),
        ]
    ),
    create=extend_schema(
        summary="Create Task",
        description="Create a new task automatically assigned to the authenticated user."
    ),
    retrieve=extend_schema(
        summary="Get Task Detail",
        description="Get specific task details by task ID."
    ),
    update=extend_schema(
        summary="Update Task",
        description="Update an existing task."
    ),
    partial_update=extend_schema(
        summary="Partial Update Task",
        description="Partially update specific fields of a task."
    ),
    destroy=extend_schema(
        summary="Delete Task",
        description="Delete a task belonging to the authenticated user."
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks with full CRUD and status toggling for the authenticated user.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(user=user)

        # Search filter
        query = self.request.query_params.get('q', '').strip()
        if query:
            queryset = queryset.filter(title__icontains=query) | queryset.filter(description__icontains=query)

        # Status filter
        status_param = self.request.query_params.get('status', 'all').lower()
        if status_param == 'completed':
            queryset = queryset.filter(completed=True)
        elif status_param == 'pending':
            queryset = queryset.filter(completed=False)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Toggle Task Status",
        description="Toggle task between completed and pending.",
        request=None,
        responses={200: TaskSerializer}
    )
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        task = self.get_object()
        task.completed = not task.completed
        task.save()
        serializer = self.get_serializer(task)
        return Response({
            'message': f"Task marked as {'completed' if task.completed else 'pending'}.",
            'task': serializer.data
        }, status=status.HTTP_200_OK)
