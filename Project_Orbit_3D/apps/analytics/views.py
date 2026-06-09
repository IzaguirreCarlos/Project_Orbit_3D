"""
Analytics API — Dashboard data, charts, burndown, velocity.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def executive_dashboard(request):
    """All-up stats for the executive dashboard cards."""
    from apps.projects.models import Project
    from apps.tasks.models import Task

    user = request.user
    projects = Project.objects.filter(assignments__user=user).distinct()
    tasks = Task.objects.filter(project__in=projects)
    now = timezone.now()

    return Response({
        'projects': {
            'total': projects.count(),
            'active': projects.filter(status='active').count(),
            'completed': projects.filter(status='completed').count(),
            'planning': projects.filter(status='planning').count(),
        },
        'tasks': {
            'total': tasks.count(),
            'done': tasks.filter(status='done').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'overdue': tasks.filter(deadline__lt=now, status__in=['todo', 'in_progress', 'review']).count(),
            'due_today': tasks.filter(
                deadline__date=now.date(),
                status__in=['todo', 'in_progress', 'review']
            ).count(),
        },
        'avg_progress': projects.aggregate(avg=Avg('progress'))['avg'] or 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_productivity(request):
    """Task completion per day for the last 7 days."""
    from apps.tasks.models import Task
    from apps.projects.models import Project

    user = request.user
    projects = Project.objects.filter(assignments__user=user).distinct()
    today = timezone.now().date()
    data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        completed = Task.objects.filter(
            project__in=projects,
            status='done',
            updated_at__date=day
        ).count()
        data.append({'date': str(day), 'completed': completed})
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_burndown(request, project_pk):
    """Ideal vs actual burndown for a project's active sprint."""
    from apps.projects.models import Project, Sprint
    from apps.tasks.models import Task

    try:
        project = Project.objects.get(pk=project_pk)
        sprint = Sprint.objects.filter(project=project, status='active').first()
    except Project.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    if not sprint:
        return Response({'error': 'No active sprint'}, status=404)

    total_points = Task.objects.filter(sprint=sprint).aggregate(
        total=Count('id')
    )['total']

    days = (sprint.end_date - sprint.start_date).days + 1
    ideal = [
        {
            'day': i,
            'ideal': round(total_points * (1 - i / (days - 1))) if days > 1 else 0
        }
        for i in range(days)
    ]

    return Response({
        'sprint': sprint.name,
        'start_date': str(sprint.start_date),
        'end_date': str(sprint.end_date),
        'total_tasks': total_points,
        'ideal_burndown': ideal,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_velocity(request):
    """Tasks completed per team member this week."""
    from apps.tasks.models import Task
    from apps.projects.models import Project

    user = request.user
    projects = Project.objects.filter(assignments__user=user).distinct()
    week_ago = timezone.now() - timedelta(days=7)

    velocity = (
        Task.objects.filter(
            project__in=projects,
            status='done',
            updated_at__gte=week_ago,
            assignee__isnull=False,
        )
        .values('assignee__first_name', 'assignee__last_name', 'assignee__id')
        .annotate(completed=Count('id'))
        .order_by('-completed')[:10]
    )
    return Response(list(velocity))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks_by_status(request):
    """Task count grouped by status across all user's projects."""
    from apps.tasks.models import Task
    from apps.projects.models import Project

    projects = Project.objects.filter(assignments__user=request.user).distinct()
    data = (
        Task.objects.filter(project__in=projects)
        .values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )
    return Response(list(data))
