"""
Accounts API URLs.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from . import views

urlpatterns = [
    # Auth
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='token-blacklist'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Profile
    path('me/', views.MeView.as_view(), name='me'),
    path('me/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('me/online/', views.set_online_status, name='online-status'),

    # Users
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),

    # Roles
    path('roles/', views.RoleListView.as_view(), name='role-list'),
]
