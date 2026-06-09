"""
Global template context available in all templates.
"""


def global_context(request):
    context = {
        'app_name': 'ProjectForge 3D',
        'app_version': '1.0.0',
    }
    if request.user.is_authenticated:
        from apps.messaging.models import Message
        from apps.core.models import AuditLog  # noqa
        context['unread_messages_count'] = Message.objects.filter(
            recipient=request.user, is_read=False
        ).count()
    return context
