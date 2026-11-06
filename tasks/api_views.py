from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from .models import Project, Task, TaskEvent
from .serializers import (
    ProjectSerializer, TaskSerializer, TaskEventSerializer, ChangeStatusSerializer,
)
from .services import change_status


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('project').prefetch_related('events').all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['status', 'priority', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)
        return qs

    def perform_create(self, serializer):
        task = serializer.save(owner=self.request.user)
        TaskEvent.objects.create(
            task=task, event_type='created', user=self.request.user,
        )

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        task = self.get_object()
        serializer = ChangeStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=400)
        new_status = serializer.validated_data['new_status']
        try:
            task = change_status(task, new_status, request.user)
        except ValidationError as e:
            return Response({'error': e.messages}, status=400)
        except PermissionError as e:
            return Response({'error': str(e)}, status=403)
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        task = self.get_object()
        events = task.events.all()
        return Response(TaskEventSerializer(events, many=True).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        from django.db.models import Count
        data = {
            'total': Task.objects.count(),
            'by_status': list(Task.objects.values('status').annotate(count=Count('id'))),
            'by_priority': list(Task.objects.values('priority').annotate(count=Count('id'))),
        }
        return Response(data)