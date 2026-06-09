from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list'),
    path('<uuid:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<uuid:pk>/stats/', views.project_stats, name='project-stats'),
    path('<uuid:project_pk>/assignments/', views.AssignmentListCreateView.as_view(), name='assignment-list'),
    path('<uuid:project_pk>/assignments/<uuid:pk>/', views.AssignmentDeleteView.as_view(), name='assignment-delete'),
    path('<uuid:project_pk>/sprints/', views.SprintListCreateView.as_view(), name='sprint-list'),
    path('<uuid:project_pk>/sprints/<uuid:pk>/', views.SprintDetailView.as_view(), name='sprint-detail'),
]
