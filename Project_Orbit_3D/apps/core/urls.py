from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/3d/', views.Dashboard3DView.as_view(), name='dashboard-3d'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
]
