from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'full_name', 'status', 'is_online', 'title', 'department', 'created_at']
    list_filter = ['status', 'is_staff', 'roles']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    filter_horizontal = ['roles', 'groups', 'user_permissions']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'avatar', 'bio', 'phone')}),
        ('Work', {'fields': ('title', 'department', 'joined_at', 'roles')}),
        ('Status', {'fields': ('status', 'is_online', 'last_seen')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
