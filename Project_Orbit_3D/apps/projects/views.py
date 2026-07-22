from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q

from .models import Project, Assignment, Sprint, Label
from .serializers import (
    ProjectSerializer, ProjectListSerializer,
    AssignmentSerializer, SprintSerializer, LabelSerializer,
)
from apps.core.permissions import IsProjectManager, IsProjectMember


class ProjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority']
    search_fields = ['name', 'description', 'client']
    ordering_fields = ['created_at', 'end_date', 'priority', 'progress']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.all() if user.is_superuser else (
            Project.objects.filter(assignments__user=user).distinct()
        )
        return qs.annotate(
            tasks_count=Count('tasks', distinct=True),
            members_count=Count('assignments', distinct=True),
        ).prefetch_related('assignments', 'labels')


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.all() if user.is_superuser else (
            Project.objects.filter(assignments__user=user).distinct()
        )
        return qs.annotate(
            tasks_count=Count('tasks', distinct=True),
            members_count=Count('assignments', distinct=True),
        )


class AssignmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectManager]

    def get_queryset(self):
        return Assignment.objects.filter(
            project_id=self.kwargs['project_pk']
        ).select_related('user', 'role')

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])


class AssignmentDeleteView(generics.DestroyAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectManager]

    def get_queryset(self):
        return Assignment.objects.filter(project_id=self.kwargs['project_pk'])


class SprintListCreateView(generics.ListCreateAPIView):
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Sprint.objects.filter(
            project_id=self.kwargs['project_pk'],
            project__assignments__user=self.request.user,
        ).distinct()

    def perform_create(self, serializer):
        project_qs = Project.objects.filter(
            id=self.kwargs['project_pk'], assignments__user=self.request.user
        )
        if not project_qs.exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied
        serializer.save(project_id=self.kwargs['project_pk'])


class SprintDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Sprint.objects.filter(
            project_id=self.kwargs['project_pk'],
            project__assignments__user=self.request.user,
        ).distinct()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def project_stats(request, pk):
    """Returns project stats for dashboard cards."""
    try:
        project = Project.objects.get(
            Q(assignments__user=request.user) | Q(owner=request.user), pk=pk
        ) if not request.user.is_superuser else Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    from apps.tasks.models import Task
    tasks = Task.objects.filter(project=project)
    by_status = {
        s: tasks.filter(status=s).count()
        for s in ['backlog', 'todo', 'in_progress', 'review', 'testing', 'done']
    }

    return Response({
        'project_id': str(project.id),
        'name': project.name,
        'progress': project.progress,
        'tasks_total': tasks.count(),
        'tasks_by_status': by_status,
        'members': project.assignments.count(),
        'budget': str(project.budget) if project.budget else None,
    })
