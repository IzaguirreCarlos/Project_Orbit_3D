"""
WebSocket consumers — chat and notifications.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """Handles real-time chat for DMs and project rooms."""

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.set_online(True)
        await self.accept()

        # Notify room of online status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': str(self.user.id),
                'is_online': True,
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            await self.set_online(False)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': str(self.user.id),
                    'is_online': False,
                }
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type', 'message')

        if msg_type == 'message':
            await self.handle_message(data)
        elif msg_type == 'typing':
            await self.handle_typing(data)
        elif msg_type == 'read':
            await self.mark_read(data)

    async def handle_message(self, data):
        content = data.get('content', '').strip()
        if not content:
            return

        message = await self.save_message(content, data.get('recipient_id'))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': str(message.id),
                'content': content,
                'sender_id': str(self.user.id),
                'sender_name': self.user.full_name,
                'sender_avatar': self.user.avatar_url,
                'timestamp': message.created_at.isoformat(),
            }
        )

    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_name': self.user.full_name,
                'is_typing': data.get('is_typing', False),
            }
        )

    # ─── Event handlers ──────────────────────────────────────
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({'type': 'message', **event}))

    async def typing_indicator(self, event):
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({'type': 'typing', **event}))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({'type': 'status', **event}))

    async def notification(self, event):
        await self.send(text_data=json.dumps({'type': 'notification', **event}))

    # ─── DB helpers ──────────────────────────────────────────
    @database_sync_to_async
    def save_message(self, content, recipient_id=None):
        from .models import Message
        kwargs = {'sender': self.user, 'content': content}
        if recipient_id:
            from apps.accounts.models import User
            try:
                kwargs['recipient'] = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                pass
        return Message.objects.create(**kwargs)

    @database_sync_to_async
    def mark_read(self, data):
        from .models import Message
        Message.objects.filter(
            id=data.get('message_id'),
            recipient=self.user
        ).update(is_read=True, read_at=timezone.now())

    @database_sync_to_async
    def set_online(self, status):
        from apps.accounts.models import User
        User.objects.filter(id=self.user.id).update(
            is_online=status,
            last_seen=timezone.now()
        )


class NotificationConsumer(AsyncWebsocketConsumer):
    """Personal notification channel per user."""

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'mark_read':
            await self.mark_read(data.get('notification_id'))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({'type': 'notification', **event}))

    @database_sync_to_async
    def mark_read(self, notification_id):
        from .models import Notification
        Notification.objects.filter(
            id=notification_id, recipient=self.user
        ).update(is_read=True, read_at=timezone.now())
