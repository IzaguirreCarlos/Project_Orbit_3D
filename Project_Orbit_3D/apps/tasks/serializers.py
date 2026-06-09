from rest_framework import serializers
from apps.accounts.serializers import UserSerializer
from .models import Task, Comment, Attachment, TaskHistory


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'is_edited', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'is_edited', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_url', 'original_name', 'file_size', 'mime_type',
                  'uploaded_by', 'created_at']
        read_only_fields = ['id', 'uploaded_by', 'file_size', 'mime_type', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class TaskHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TaskHistory
        fields = ['id', 'field_name', 'old_value', 'new_value', 'user', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    comments_count = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    subtasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'project', 'sprint', 'creator', 'assignee', 'assignee_id',
            'parent', 'title', 'description', 'priority', 'status',
            'deadline', 'estimated_hours', 'actual_hours', 'story_points',
            'order', 'is_blocked', 'blocked_reason', 'is_overdue',
            'comments_count', 'attachments_count', 'subtasks_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_attachments_count(self, obj):
        return obj.attachments.count()

    def get_subtasks_count(self, obj):
        return obj.subtasks.count()

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class TaskKanbanSerializer(serializers.ModelSerializer):
    """Minimal serializer for Kanban board columns."""
    assignee_name = serializers.SerializerMethodField()
    assignee_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'priority', 'status', 'deadline',
            'story_points', 'order', 'is_overdue', 'assignee_name', 'assignee_avatar',
        ]

    def get_assignee_name(self, obj):
        return obj.assignee.full_name if obj.assignee else None

    def get_assignee_avatar(self, obj):
        return obj.assignee.avatar_url if obj.assignee else None
