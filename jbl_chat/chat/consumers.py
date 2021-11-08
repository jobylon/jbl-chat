import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message, AppUsersConnected
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope["user"]
        print(self.user)
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print('Websocket disconnected: ' + str(close_code))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        pass

    async def receive(self, text_data):
        json_message = json.loads(text_data)
        message = json_message['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class UserChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        print(self.scope['url_route']['kwargs'])
        self.room_name = self.scope['url_route']['kwargs']['user_room_name']
        print(self.scope['url_route']['kwargs'])
        self.user = self.scope["user"]
        print(self.user)
        self.room_group_name = 'chat_%s' % self.user
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print('Websocket disconnected: ' + str(close_code))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        pass

    async def receive(self, text_data):
        json_message = json.loads(text_data)
        message = json_message['message']

        await self.save_message(message, self.user, self.room_name, self.room_group_name)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        # Send message to room group
        await self.channel_layer.group_send(
            'chat_%s' % self.room_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @sync_to_async
    def save_message(self, message, sender, receiver, room):
        Message.save_message(message, sender, receiver, room)


class AppChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = 'chat'
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        await self.connect_user(user=self.user)

        users = await self.logged_users()
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': users
            }
        )

    async def disconnect(self, close_code):
        print('Websocket disconnected: ' + str(close_code))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.disconnect_user(user=self.user)

    async def receive(self, text_data):
        json_message = json.loads(text_data)
        message = json_message['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):

        users = await self.logged_users()
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': users
        }))

    @sync_to_async
    def connect_user(self, user):
        if user:
            AppUsersConnected.objects.create(user=user)
        else:
            pass
        return None

    @sync_to_async
    def disconnect_user(self, user):
        try:
            user = AppUsersConnected.objects.filter(user=user)[0]
        except:
            pass
        else:
            user.delete()

    @sync_to_async
    def logged_users(self):
        return [{'username': user.user.username} for user in AppUsersConnected.logged_users()]
