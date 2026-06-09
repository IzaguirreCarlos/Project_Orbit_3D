"""
Accounts — User and Role models.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from apps.core.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 'active')
        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    """Organizational roles."""
    ROLE_CHOICES = [
        ('CEO', 'CEO'),
        ('CTO', 'CTO'),
        ('Project Manager', 'Project Manager'),
        ('Scrum Master', 'Scrum Master'),
        ('Team Lead', 'Team Lead'),
        ('Backend Developer', 'Backend Developer'),
        ('Frontend Developer', 'Frontend Developer'),
        ('QA Engineer', 'QA Engineer'),
        ('UI/UX Designer', 'UI/UX Designer'),
        ('DevOps Engineer', 'DevOps Engineer'),
        ('Client', 'Client'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_role'
        ordering = ['name']

    def __str__(self):
        return self.name


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """Custom user model with profile fields."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    joined_at = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    roles = models.ManyToManyField(Role, blank=True, related_name='users')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'accounts_user'
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        import base64
        initials = (
            f'{self.first_name[0]}{self.last_name[0]}'.upper()
            if self.first_name else '?'
        )
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128">'
            '<rect width="128" height="128" fill="#6366f1" rx="64"/>'
            f'<text x="64" y="64" dominant-baseline="central" text-anchor="middle" '
            f'fill="white" font-size="52" font-family="sans-serif">{initials}</text>'
            '</svg>'
        )
        encoded = base64.b64encode(svg.encode()).decode()
        return f'data:image/svg+xml;base64,{encoded}'

    def get_primary_role(self):
        from apps.core.permissions import ROLE_HIERARCHY
        best = None
        best_level = -1
        for role in self.roles.all():
            level = ROLE_HIERARCHY.get(role.name, 0)
            if level > best_level:
                best_level = level
                best = role
        return best
