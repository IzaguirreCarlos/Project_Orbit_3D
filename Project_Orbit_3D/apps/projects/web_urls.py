from django.urls import path
from . import web_views

app_name = 'projects'

urlpatterns = [
    path('', web_views.ProjectListView.as_view(), name='list'),
    path('new/', web_views.ProjectCreateView.as_view(), name='create'),
    path('<uuid:pk>/', web_views.ProjectDetailView.as_view(), name='detail'),
    path('<uuid:pk>/kanban/', web_views.KanbanView.as_view(), name='kanban'),
    path('<uuid:pk>/timeline/', web_views.TimelineView.as_view(), name='timeline'),
]
