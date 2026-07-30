"""
reset_admin — Fuerza el reset completo del superusuario admin.
Úsalo cuando no puedas entrar al sistema:
    python manage.py reset_admin
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User


ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@projectforge.com"
ADMIN_PASSWORD = "Admin12345!"


class Command(BaseCommand):
    help = "Fuerza el reset de credenciales del superusuario admin"

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default=ADMIN_PASSWORD,
            help=f'Nueva contraseña (default: {ADMIN_PASSWORD})',
        )

    def handle(self, *args, **options):
        new_password = options['password']

        # Buscar por username o email
        user = (
            User.objects.filter(username=ADMIN_USERNAME).first()
            or User.objects.filter(email=ADMIN_EMAIL).first()
        )

        if user is None:
            user = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                first_name="Admin",
                last_name="ProjectForge",
                is_staff=True,
                is_superuser=True,
                is_active=True,
                status="active",
            )
            user.set_password(new_password)
            user.save()
            self.stdout.write(self.style.SUCCESS("Usuario admin CREADO desde cero."))
        else:
            user.username = ADMIN_USERNAME
            user.email = ADMIN_EMAIL
            user.first_name = "Admin"
            user.last_name = "ProjectForge"
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.status = "active"
            user.set_password(new_password)
            user.save()
            self.stdout.write(self.style.SUCCESS("Usuario admin RESETEADO correctamente."))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("═" * 40))
        self.stdout.write(self.style.SUCCESS("  CREDENCIALES DE ACCESO"))
        self.stdout.write(self.style.SUCCESS("═" * 40))
        self.stdout.write(f"  URL:       http://localhost:8000/accounts/login/")
        self.stdout.write(f"  Admin:     http://localhost:8000/admin/")
        self.stdout.write(f"  Username:  {ADMIN_USERNAME}")
        self.stdout.write(f"  Email:     {ADMIN_EMAIL}")
        self.stdout.write(f"  Password:  {new_password}")
        self.stdout.write(self.style.SUCCESS("═" * 40))
