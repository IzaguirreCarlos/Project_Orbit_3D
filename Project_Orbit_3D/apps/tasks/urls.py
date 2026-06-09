from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListCreateView.as_view(), name='task-list'),
    path('<uuid:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<uuid:pk>/move/', views.move_task, name='task-move'),
    path('<uuid:task_pk>/comments/', views.CommentListCreateView.as_view(), name='comment-list'),
    path('<uuid:task_pk>/comments/<uuid:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('<uuid:task_pk>/attachments/', views.AttachmentCreateView.as_view(), name='attachment-create'),
    path('<uuid:task_pk>/history/', views.TaskHistoryView.as_view(), name='task-history'),
    path('kanban/<uuid:project_pk>/', views.kanban_board, name='kanban-board'),
]
