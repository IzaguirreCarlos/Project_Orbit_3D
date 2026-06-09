from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task


@receiver(post_save, sender=Task)
def notify_on_assignment(sender, instance, created, **kwargs):
    """Send notification when a task is assigned."""
    if instance.assignee and (created or getattr(instance, '_assignee_changed', False)):
        from apps.messaging.tasks import send_task_notification
        send_task_notification.delay(
            task_id=str(instance.id),
            recipient_id=str(instance.assignee.id),
            event='assigned',
        )
