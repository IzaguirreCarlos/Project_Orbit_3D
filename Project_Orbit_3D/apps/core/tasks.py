"""
Core Celery tasks.
"""
from celery import shared_task
import logging

logger = logging.getLogger('apps.core')


@shared_task(bind=True, max_retries=3)
def create_audit_log(self, user_id, action, resource_type,
                     resource_id='', ip_address=None, user_agent=''):
    try:
        from apps.core.models import AuditLog
        AuditLog.objects.create(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception as exc:
        logger.error('create_audit_log failed: %s', exc)
        raise self.retry(exc=exc, countdown=5)
