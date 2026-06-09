"""
Custom DRF permissions for role-based access control.
"""
from rest_framework.permissions import BasePermission

ROLE_HIERARCHY = {
    'CEO': 100,
    'CTO': 90,
    'Project Manager': 70,
    'Scrum Master': 60,
    'Team Lead': 50,
    'Backend Developer': 30,
    'Frontend Developer': 30,
    'QA Engineer': 30,
    'UI/UX Designer': 30,
    'DevOps Engineer': 30,
    'Client': 10,
}


def get_user_role_level(user):
    """Returns the highest role level of a user."""
    if user.is_superuser:
        return 999
    level = 0
    for role in user.roles.all():
        level = max(level, ROLE_HIERARCHY.get(role.name, 0))
    return level


class IsExecutive(BasePermission):
    """CEO or CTO."""
    def has_permission(self, request, view):
        return get_user_role_level(request.user) >= 90


class IsProjectManager(BasePermission):
    """PM or above."""
    def has_permission(self, request, view):
        return get_user_role_level(request.user) >= 70


class IsTeamLead(BasePermission):
    """Team Lead or above."""
    def has_permission(self, request, view):
        return get_user_role_level(request.user) >= 50


class IsDeveloper(BasePermission):
    """Any developer-level role or above."""
    def has_permission(self, request, view):
        return get_user_role_level(request.user) >= 30


class IsProjectMember(BasePermission):
    """User is assigned to the project."""
    def has_object_permission(self, request, view, obj):
        project = getattr(obj, 'project', obj)
        return project.assignments.filter(user=request.user).exists()


class IsClientOrAbove(BasePermission):
    """Any authenticated user with a role."""
    def has_permission(self, request, view):
        return get_user_role_level(request.user) >= 10
