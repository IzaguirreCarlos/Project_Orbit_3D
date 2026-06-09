"""
Helper functions to push notifications via Channel Layer.
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def push_notification(user_id, notification_type, title, body='', action_url='', metadata=None):
    """Create a Notification record and push it via WebSocket."""
    from .models import Notification
    notif = Notification.objects.create(
        recipient_id=user_id,
        notification_type=notification_type,
        title=title,
        body=body,
        action_url=action_url,
        metadata=metadata or {},
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'send_notification',
            'id': str(notif.id),
            'notification_type': notification_type,
            'title': title,
            'body': body,
            'action_url': action_url,
        }
    )
    return notif


def notify_task_moved(task, old_status, new_status, moved_by):
    """Notify task assignee when a task is moved to a new column."""
    if task.assignee and task.assignee != moved_by:
        push_notification(
            user_id=str(task.assignee.id),
            notification_type='task_assigned',
            title=f'Task "{task.title}" moved to {new_status}',
            body=f'Moved by {moved_by.full_name} from {old_status} → {new_status}',
            action_url=f'/projects/{task.project_id}/kanban/',
        )
