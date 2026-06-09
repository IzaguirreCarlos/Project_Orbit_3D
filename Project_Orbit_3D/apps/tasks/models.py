"""
Tasks — Task, Comment, Attachment, ChangeHistory models.
"""
from django.db import models
from apps.core.models import BaseModel


class Task(BaseModel):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('testing', 'Testing'),
        ('done', 'Done'),
    ]

    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='tasks'
    )
    sprint = models.ForeignKey(
        'projects.Sprint', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tasks'
    )
    creator = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True,
        related_name='created_tasks'
    )
    assignee = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tasks'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='subtasks'
    )
    labels = models.ManyToManyField('projects.Label', blank=True, related_name='tasks')

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    deadline = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    story_points = models.PositiveSmallIntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'tasks_task'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk:
            prev_assignee = (
                Task.objects.filter(pk=self.pk)
                .values_list('assignee_id', flat=True)
                .first()
            )
            self._assignee_changed = prev_assignee != self.assignee_id
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.deadline and self.status != 'done':
            return self.deadline < timezone.now()
        return False


class Comment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_edited = models.BooleanField(default=False)

    class Meta:
        db_table = 'tasks_comment'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} on {self.task}: {self.content[:50]}'


class Attachment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='uploads'
    )
    file = models.FileField(upload_to='attachments/%Y/%m/')
    original_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'tasks_attachment'
        ordering = ['-created_at']

    def __str__(self):
        return self.original_name


class TaskHistory(BaseModel):
    """Immutable record of every change to a task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='task_changes'
    )
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)

    class Meta:
        db_table = 'tasks_history'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task.title}: {self.field_name} changed by {self.user}'
