from django.urls import path
from django.contrib.auth import views as auth_views
from . import web_views

urlpatterns = [
    path('login/', web_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('register/', web_views.RegisterView.as_view(), name='register'),
    path('profile/', web_views.ProfileView.as_view(), name='profile'),
    path('team/', web_views.TeamView.as_view(), name='team'),
]
