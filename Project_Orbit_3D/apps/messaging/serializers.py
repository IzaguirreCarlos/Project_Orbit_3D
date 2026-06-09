from rest_framework import serializers
from apps.accounts.serializers import UserSerializer
from .models import Message, Notification


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    recipient_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient', 'recipient_id', 'project',
            'content', 'is_read', 'read_at', 'is_edited', 'created_at',
        ]
        read_only_fields = ['id', 'sender', 'is_read', 'read_at', 'is_edited', 'created_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'body', 'is_read',
            'read_at', 'action_url', 'metadata', 'created_at',
        ]
        read_only_fields = fields
