from celery import shared_task
import logging

logger = logging.getLogger('apps.messaging')


@shared_task(bind=True, max_retries=3)
def send_task_notification(self, task_id, recipient_id, event):
    try:
        from apps.tasks.models import Task
        task = Task.objects.select_related('project', 'assignee', 'creator').get(id=task_id)

        messages = {
            'assigned': (
                f'New task: {task.title}',
                f'Assigned to you in {task.project.name} · Priority: {task.priority}'
            ),
            'due_soon': (
                f'Task due soon: {task.title}',
                f'Due: {task.deadline}'
            ),
            'overdue': (
                f'⚠️ Overdue: {task.title}',
                f'This task is past its deadline'
            ),
        }

        title, body = messages.get(event, (f'Task update: {task.title}', ''))
        from .notifications import push_notification
        push_notification(
            user_id=recipient_id,
            notification_type='task_assigned',
            title=title,
            body=body,
            action_url=f'/tasks/{task_id}/',
            metadata={'task_id': task_id, 'project_id': str(task.project_id)},
        )
    except Exception as exc:
        logger.error('send_task_notification failed: %s', exc)
        raise self.retry(exc=exc, countdown=10)


@shared_task
def check_overdue_tasks():
    """Celery beat task — runs every hour to detect overdue tasks."""
    from django.utils import timezone
    from apps.tasks.models import Task
    overdue = Task.objects.filter(
        deadline__lt=timezone.now(),
        status__in=['todo', 'in_progress', 'review'],
    ).select_related('assignee')

    for task in overdue:
        if task.assignee:
            send_task_notification.delay(
                str(task.id), str(task.assignee.id), 'overdue'
            )
