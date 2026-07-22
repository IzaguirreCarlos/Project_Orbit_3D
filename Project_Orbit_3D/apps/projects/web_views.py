from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView
from .models import Project


def _get_accessible_project(user, pk):
    qs = Project.objects.all() if user.is_superuser else Project.objects.filter(
        Q(assignments__user=user) | Q(owner=user)
    ).distinct()
    return get_object_or_404(qs, pk=pk)


class ProjectListView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/list.html'


class ProjectCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/create.html'


class ProjectDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['project'] = _get_accessible_project(self.request.user, self.kwargs['pk'])
        return ctx


class KanbanView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/kanban.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['project'] = _get_accessible_project(self.request.user, self.kwargs['pk'])
        return ctx


class TimelineView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/timeline.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['project'] = _get_accessible_project(self.request.user, self.kwargs['pk'])
        return ctx
