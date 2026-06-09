from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.executive_dashboard, name='exec-dashboard'),
    path('productivity/weekly/', views.weekly_productivity, name='weekly-productivity'),
    path('projects/<uuid:project_pk>/burndown/', views.project_burndown, name='project-burndown'),
    path('team/velocity/', views.team_velocity, name='team-velocity'),
    path('tasks/by-status/', views.tasks_by_status, name='tasks-by-status'),
]
