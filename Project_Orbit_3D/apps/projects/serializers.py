from rest_framework import serializers
from apps.accounts.serializers import UserSerializer, RoleSerializer
from .models import Project, Assignment, Sprint, Label


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name', 'color']


class AssignmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    role = RoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Assignment
        fields = ['id', 'user', 'user_id', 'role', 'role_id', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']


class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = [
            'id', 'project', 'name', 'goal', 'start_date',
            'end_date', 'status', 'velocity', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.UUIDField(write_only=True, required=False)
    assignments = AssignmentSerializer(many=True, read_only=True)
    labels = LabelSerializer(many=True, read_only=True)
    tasks_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'client', 'owner', 'owner_id',
            'start_date', 'end_date', 'budget', 'priority', 'status',
            'progress', 'theme_color', 'icon', 'repository_url',
            'documentation_url', 'tags', 'assignments', 'labels',
            'tasks_count', 'members_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'progress', 'created_at', 'updated_at']

    def get_tasks_count(self, obj):
        if hasattr(obj, 'tasks_count'):
            return obj.tasks_count
        return obj.tasks.count()

    def get_members_count(self, obj):
        if hasattr(obj, 'members_count'):
            return obj.members_count
        return obj.assignments.count()

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    tasks_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'client', 'status', 'priority', 'progress',
            'theme_color', 'icon', 'end_date', 'tasks_count', 'members_count',
        ]

    def get_tasks_count(self, obj):
        if hasattr(obj, 'tasks_count'):
            return obj.tasks_count
        return obj.tasks.count()

    def get_members_count(self, obj):
        if hasattr(obj, 'members_count'):
            return obj.members_count
        return obj.assignments.count()
