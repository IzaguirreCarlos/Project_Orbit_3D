from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView


class HealthCheckView(View):
    """Render health check — verifica DB y responde 200."""

    def get(self, request):
        try:
            connection.ensure_connection()
            db_ok = True
        except Exception:
            db_ok = False

        status = 200 if db_ok else 503
        return JsonResponse({'status': 'ok' if db_ok else 'error', 'db': db_ok}, status=status)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.projects.models import Project
        from apps.tasks.models import Task

        user = self.request.user
        ctx['active_projects'] = Project.objects.filter(
            Q(assignments__user=user) | Q(owner=user),
            status__in=['planning', 'active', 'in_review']
        ).distinct()[:6]
        ctx['pending_tasks'] = Task.objects.filter(
            assignee=user,
            status__in=['todo', 'in_progress', 'review']
        ).order_by('deadline')[:10]
        ctx['completed_tasks_count'] = Task.objects.filter(
            assignee=user, status='done'
        ).count()
        return ctx


class Dashboard3DView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/3d.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.projects.models import Project
        import json
        projects = Project.objects.filter(
            Q(assignments__user=self.request.user) | Q(owner=self.request.user)
        ).distinct().values(
            'id', 'name', 'status', 'progress', 'theme_color', 'priority'
        )
        ctx['projects_json'] = json.dumps(list(projects), default=str)
        return ctx


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/index.html'
