"""
Messaging — Message and Notification models.
"""
from django.db import models
from apps.core.models import BaseModel


class Message(BaseModel):
    sender = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='received_messages',
        null=True, blank=True
    )
    # For group messages (project-wide)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='messages',
        null=True, blank=True
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        db_table = 'messaging_message'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient', '-created_at']),
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f'{self.sender} → {self.recipient or self.project}: {self.content[:50]}'


class Notification(BaseModel):
    TYPE_CHOICES = [
        ('task_assigned', 'Task Assigned'),
        ('task_due', 'Task Due Soon'),
        ('task_overdue', 'Task Overdue'),
        ('project_status', 'Project Status Changed'),
        ('message', 'New Message'),
        ('mention', 'Mentioned'),
        ('comment', 'New Comment'),
    ]

    recipient = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'messaging_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f'{self.notification_type} → {self.recipient}'
