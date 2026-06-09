"""
Projects — Project, Assignment, Sprint, Label models.
"""
from django.db import models
from apps.core.models import BaseModel


class Project(BaseModel):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('in_review', 'In Review'),
        ('testing', 'Testing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    client = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_projects'
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    progress = models.PositiveSmallIntegerField(default=0)  # 0-100
    theme_color = models.CharField(max_length=7, default='#6366f1')  # hex
    icon = models.CharField(max_length=50, default='rocket')
    repository_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'projects_project'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return self.name

    def update_progress(self):
        """Recalculate progress from completed tasks."""
        from apps.tasks.models import Task
        total = Task.objects.filter(project=self).count()
        if total == 0:
            self.progress = 0
        else:
            done = Task.objects.filter(project=self, status='done').count()
            self.progress = int((done / total) * 100)
        self.save(update_fields=['progress'])


class Assignment(BaseModel):
    """Links a user to a project with a specific role."""
    user = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='assignments'
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='assignments'
    )
    role = models.ForeignKey(
        'accounts.Role', on_delete=models.SET_NULL, null=True, related_name='assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projects_assignment'
        unique_together = [('user', 'project')]
        ordering = ['assigned_at']

    def __str__(self):
        return f'{self.user} → {self.project} ({self.role})'


class Sprint(BaseModel):
    """Scrum Sprint linked to a project."""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sprints')
    name = models.CharField(max_length=100)
    goal = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    velocity = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'projects_sprint'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.project.name} — {self.name}'


class Label(BaseModel):
    """Colored labels for projects."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labels')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#6366f1')

    class Meta:
        db_table = 'projects_label'
        unique_together = [('project', 'name')]

    def __str__(self):
        return f'{self.project.name} / {self.name}'
