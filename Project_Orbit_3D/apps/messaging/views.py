from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Message, Notification
from .serializers import MessageSerializer, NotificationSerializer


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        recipient_id = self.request.query_params.get('recipient_id')
        project_id = self.request.query_params.get('project_id')
        qs = Message.objects.select_related('sender', 'recipient')
        if recipient_id:
            qs = qs.filter(
                sender__in=[user.id, recipient_id],
                recipient__in=[user.id, recipient_id]
            )
        elif project_id:
            qs = qs.filter(project_id=project_id)
        else:
            qs = qs.filter(recipient=user)
        return qs.order_by('created_at')


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True, read_at=timezone.now())
    return Response({'status': 'ok'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_counts(request):
    return Response({
        'messages': Message.objects.filter(recipient=request.user, is_read=False).count(),
        'notifications': Notification.objects.filter(recipient=request.user, is_read=False).count(),
    })
