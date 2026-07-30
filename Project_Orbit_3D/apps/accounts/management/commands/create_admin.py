from django.core.management.base import BaseCommand
from apps.accounts.models import User


ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@projectforge.com"
ADMIN_PASSWORD = "Admin12345!"
ADMIN_FIRST_NAME = "Admin"
ADMIN_LAST_NAME = "ProjectForge"


class Command(BaseCommand):
    help = "Create or restore the default admin superuser"

    def handle(self, *args, **kwargs):
        user = User.objects.filter(username=ADMIN_USERNAME).first()

        if user is None:
            # Intentar también por email (puede existir con otro username)
            user = User.objects.filter(email=ADMIN_EMAIL).first()

        if user is None:
            user = User.objects.create_superuser(  # type: ignore
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD,
                first_name=ADMIN_FIRST_NAME,
                last_name=ADMIN_LAST_NAME,
            )
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Admin creado — username: {ADMIN_USERNAME} | password: {ADMIN_PASSWORD}"
            ))
        else:
            # Garantizar que tenga todos los permisos y la password correcta
            user.username = ADMIN_USERNAME
            user.email = ADMIN_EMAIL
            user.first_name = ADMIN_FIRST_NAME
            user.last_name = ADMIN_LAST_NAME
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.status = "active"
            user.set_password(ADMIN_PASSWORD)
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Admin actualizado — username: {ADMIN_USERNAME} | password: {ADMIN_PASSWORD}"
            ))