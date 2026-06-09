"""
Core middleware — Audit logging.
"""
import logging

logger = logging.getLogger('apps.core')


class AuditLogMiddleware:
    """Logs mutating API requests to AuditLog asynchronously."""
    LOGGED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.method in self.LOGGED_METHODS
            and request.path.startswith('/api/')
            and hasattr(request, 'user')
            and request.user.is_authenticated
        ):
            self._log(request, response)

        return response

    def _log(self, request, response):
        try:
            from apps.core.tasks import create_audit_log
            create_audit_log.delay(
                user_id=str(request.user.id),
                action=request.method,
                resource_type=request.path.split('/')[3] if len(request.path.split('/')) > 3 else 'unknown',
                ip_address=self._get_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
        except Exception as exc:
            logger.warning('AuditLog failed: %s', exc)

    @staticmethod
    def _get_ip(request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
