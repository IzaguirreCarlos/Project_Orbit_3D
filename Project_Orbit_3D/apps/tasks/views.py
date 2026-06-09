from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from .models import Task, Comment, Attachment, TaskHistory
from .serializers import (
    TaskSerializer, TaskKanbanSerializer,
    CommentSerializer, AttachmentSerializer, TaskHistorySerializer,
)


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'status', 'priority', 'assignee', 'sprint']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'deadline', 'priority', 'created_at']

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(project__assignments__user=user) | Q(project__owner=user)
        ).select_related('assignee', 'creator', 'project').distinct()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(project__assignments__user=user) | Q(project__owner=user)
        ).distinct()

    def perform_update(self, serializer):
        old = self.get_object()
        instance = serializer.save()
        # Record status change history
        for field in ['status', 'priority', 'assignee', 'deadline']:
            old_val = str(getattr(old, field, '') or '')
            new_val = str(getattr(instance, field, '') or '')
            if old_val != new_val:
                TaskHistory.objects.create(
                    task=instance,
                    user=self.request.user,
                    field_name=field,
                    old_value=old_val,
                    new_value=new_val,
                )
        # Update project progress on status change
        if old.status != instance.status:
            instance.project.update_progress()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def kanban_board(request, project_pk):
    """Returns tasks grouped by status for the Kanban board."""
    tasks = Task.objects.filter(
        project_id=project_pk,
        project__assignments__user=request.user,
        parent=None,  # only top-level tasks
    ).select_related('assignee').distinct().order_by('order')

    columns = {s: [] for s, _ in Task.STATUS_CHOICES}
    serializer = TaskKanbanSerializer(tasks, many=True)
    for task in serializer.data:
        columns[task['status']].append(task)

    return Response(columns)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def move_task(request, pk):
    """Move a task to a different status column."""
    try:
        task = Task.objects.get(pk=pk, project__assignments__user=request.user)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    new_order = request.data.get('order', task.order)
    if new_status not in dict(Task.STATUS_CHOICES):
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    old_status = task.status
    task.status = new_status
    task.order = new_order
    task.save(update_fields=['status', 'order'])

    if old_status != new_status:
        task.project.update_progress()
        # Send WebSocket notification
        from apps.messaging.notifications import notify_task_moved
        notify_task_moved(task, old_status, new_status, request.user)

    return Response(TaskKanbanSerializer(task).data)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(
            task_id=self.kwargs['task_pk'],
            task__project__assignments__user=self.request.user,
        ).select_related('author').distinct()

    def perform_create(self, serializer):
        task_qs = Task.objects.filter(
            id=self.kwargs['task_pk'],
            project__assignments__user=self.request.user,
        ).distinct()
        if not task_qs.exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied
        serializer.save(task_id=self.kwargs['task_pk'], author=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(
            task__project__assignments__user=self.request.user,
        ).distinct()

    def perform_update(self, serializer):
        serializer.save(is_edited=True)


class AttachmentCreateView(generics.CreateAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        f = self.request.FILES.get('file')
        serializer.save(
            task_id=self.kwargs['task_pk'],
            uploaded_by=self.request.user,
            original_name=f.name if f else '',
            file_size=f.size if f else 0,
            mime_type=f.content_type if f else '',
        )


class TaskHistoryView(generics.ListAPIView):
    serializer_class = TaskHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskHistory.objects.filter(
            task_id=self.kwargs['task_pk']
        ).select_related('user')
