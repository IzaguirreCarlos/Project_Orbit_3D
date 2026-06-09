from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.MessageListCreateView.as_view(), name='message-list'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='notifications-read-all'),
    path('unread/', views.unread_counts, name='unread-counts'),
]
