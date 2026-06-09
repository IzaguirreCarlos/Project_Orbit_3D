from django.contrib import admin
from .models import Task, Comment, Attachment, TaskHistory


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['author', 'created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assignee', 'deadline', 'is_overdue']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['title', 'description']
    raw_id_fields = ['project', 'assignee', 'creator', 'sprint']
    inlines = [CommentInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ['task', 'field_name', 'old_value', 'new_value', 'user', 'created_at']
    readonly_fields = ['task', 'user', 'field_name', 'old_value', 'new_value', 'created_at']
