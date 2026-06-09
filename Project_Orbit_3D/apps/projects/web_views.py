from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from .models import Project


class ProjectListView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/list.html'


class ProjectCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/create.html'


class ProjectDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return ctx


class KanbanView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/kanban.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return ctx


class TimelineView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/timeline.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return ctx
