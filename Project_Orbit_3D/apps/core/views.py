from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.projects.models import Project
        from apps.tasks.models import Task

        user = self.request.user
        ctx['active_projects'] = Project.objects.filter(
            assignments__user=user,
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
            assignments__user=self.request.user
        ).distinct().values(
            'id', 'name', 'status', 'progress', 'theme_color', 'priority'
        )
        ctx['projects_json'] = json.dumps(list(projects), default=str)
        return ctx


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/index.html'
