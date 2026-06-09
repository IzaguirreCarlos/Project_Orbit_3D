from django.contrib import admin
from .models import Project, Assignment, Sprint, Label


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    raw_id_fields = ['user', 'role']


class SprintInline(admin.TabularInline):
    model = Sprint
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'status', 'priority', 'progress', 'owner', 'end_date']
    list_filter = ['status', 'priority']
    search_fields = ['name', 'client', 'description']
    inlines = [AssignmentInline, SprintInline]
    readonly_fields = ['progress', 'created_at', 'updated_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'role', 'assigned_at']
    list_filter = ['role']
    search_fields = ['user__email', 'project__name']


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'start_date', 'end_date']
    list_filter = ['status']
