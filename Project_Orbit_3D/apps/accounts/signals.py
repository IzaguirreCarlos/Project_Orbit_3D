from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """Assign 'Client' role to new users if no role is set."""
    if created and not instance.roles.exists():
        from .models import Role
        try:
            client_role, _ = Role.objects.get_or_create(name='Client')
            instance.roles.add(client_role)
        except Exception:
            pass
